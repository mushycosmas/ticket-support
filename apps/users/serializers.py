from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Team
from apps.tickets.models import Ticket

User = get_user_model()


# ======================
# 👤 USER SERIALIZER
# ======================
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',

            # 🏅 HRMIS ADDITIONS
            'rank',
            'profile_picture',

            # 🔐 SYSTEM
            'role',
            'is_active',
            'is_staff',
            'is_superuser',
            'last_login',
            'date_joined',

            # 👥 TEAMS (M2M FIXED)
            'team_name',
        ]

        read_only_fields = ['id', 'last_login', 'date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_team_name(self, obj):
        # ManyToMany FIX
        if hasattr(obj, 'teams'):
            return [team.name for team in obj.teams.all()]
        return []


# ======================
# 👤 CREATE USER
# ======================
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',

            # 🏅 HRMIS ADDITIONS
            'rank',
            'profile_picture',

            'role',
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match"}
            )
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ======================
# 👤 UPDATE USER
# ======================
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'role',
            'rank',
            'profile_picture',
            'is_active',
        ]


# ======================
# 🎟️ USER TICKETS
# ======================
class UserTicketSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id',
            'ticket_number',
            'title',
            'description',
            'status',
            'priority',
            'created_at',
            'updated_at',
            'resolved_at',
            'customer_name',
            'assigned_to_name'
        ]

    def get_customer_name(self, obj):
        return obj.customer.full_name if obj.customer else None

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name() if obj.assigned_to else None


# ======================
# 📊 USER STATS
# ======================
class UserStatsSerializer(serializers.Serializer):
    total_assigned = serializers.IntegerField()
    total_open = serializers.IntegerField()
    total_in_progress = serializers.IntegerField()
    total_resolved = serializers.IntegerField()
    total_closed = serializers.IntegerField()


# ======================
# 👥 TEAM SERIALIZER
# ======================
class TeamSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id',
            'name',
            'description',
            'member_count'
        ]
        read_only_fields = ['id']

    def get_member_count(self, obj):
        return obj.members.count()


class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'description']


class TeamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'description']


# ======================
# 👥 TEAM MEMBERS
# ======================
class TeamMemberSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',

            # 🏅 HRMIS
            'rank',
            'profile_picture',
            'role',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username