# apps/roles/serializers.py - CORRECT VERSION
from rest_framework import serializers
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Role


class PermissionSerializer(serializers.ModelSerializer):
    # Make content_type_id required only for create, optional for update
    content_type_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type_id']
        extra_kwargs = {
            'content_type_id': {'required': False}
        }

    def create(self, validated_data):
        # content_type_id is required for create
        content_type_id = validated_data.pop('content_type_id', None)
        
        if content_type_id is None:
            raise serializers.ValidationError({
                'content_type_id': 'This field is required for creating permissions.'
            })
        
        try:
            content_type = ContentType.objects.get(id=content_type_id)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError({
                'content_type_id': f'ContentType with id {content_type_id} does not exist'
            })
        
        # Create permission with the content_type
        permission = Permission.objects.create(
            name=validated_data['name'],
            codename=validated_data['codename'],
            content_type=content_type
        )
        return permission

    def update(self, instance, validated_data):
        # content_type_id is optional for update
        content_type_id = validated_data.pop('content_type_id', None)
        
        if content_type_id is not None:
            try:
                content_type = ContentType.objects.get(id=content_type_id)
                instance.content_type = content_type
            except ContentType.DoesNotExist:
                raise serializers.ValidationError({
                    'content_type_id': f'ContentType with id {content_type_id} does not exist'
                })
        
        # Update other fields
        instance.name = validated_data.get('name', instance.name)
        instance.codename = validated_data.get('codename', instance.codename)
        instance.save()
        return instance


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False
    )
    permission_details = PermissionSerializer(
        source='permissions', 
        many=True, 
        read_only=True
    )

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'is_active', 
            'permissions', 'permission_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        role = Role.objects.create(**validated_data)
        role.permissions.set(permissions)
        return role

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permissions', None)
        
        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update permissions if provided
        if permissions is not None:
            instance.permissions.set(permissions)
        
        return instance