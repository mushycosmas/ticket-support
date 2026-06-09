# apps/roles/serializers.py - CORRECT VERSION
from rest_framework import serializers
from django.contrib.auth.models import Permission
from .models import Role  # ← Import Role from models, don't define it here


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']


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
        model = Role  # ← This should reference the model, not define it
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