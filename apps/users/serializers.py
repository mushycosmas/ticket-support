from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Team

User = get_user_model()


class TeamSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'lead', 'member_count', 'created_at']
    
    def get_member_count(self, obj):
        return obj.members.count() if hasattr(obj, 'members') else 0


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'team', 'team_name', 'is_active', 'is_staff', 'is_superuser',
            'last_login', 'date_joined'
        ]
        read_only_fields = ['id', 'last_login', 'date_joined']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    
    def get_team_name(self, obj):
        if obj.team:
            return obj.team.name
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        
        if len(data['password']) < 6:
            raise serializers.ValidationError({"password": "Password must be at least 6 characters"})
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'team', 'is_active']


class UserTicketSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ticket_number = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    status = serializers.CharField()
    priority = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    resolved_at = serializers.DateTimeField(allow_null=True)
    customer_name = serializers.SerializerMethodField()
    
    def get_customer_name(self, obj):
        if hasattr(obj, 'customer') and obj.customer:
            return obj.customer.full_name
        return None


class UserStatsSerializer(serializers.Serializer):
    total_assigned = serializers.IntegerField()
    total_open = serializers.IntegerField()
    total_in_progress = serializers.IntegerField()
    total_resolved = serializers.IntegerField()
    total_closed = serializers.IntegerField()