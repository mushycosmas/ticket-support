from rest_framework import serializers
from .models import User, Team


# =========================
# TEAM SERIALIZER
# =========================
class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = [
            'id',
            'name',
            'description',
            'created_at'
        ]


# =========================
# USER SERIALIZER
# =========================
class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True)

    # read-only helper (for frontend display)
    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'phone',
            'role',
            'team',
            'team_name',
            'is_active',
            'date_joined',
        ]

        read_only_fields = ['id', 'date_joined']

    # =========================
    # CREATE USER (IMPORTANT FIX)
    # =========================
    def create(self, validated_data):

        password = validated_data.pop('password', None)

        # default password fallback (your request: support123)
        if not password:
            password = "support123"

        user = User(**validated_data)
        user.set_password(password)  # always hash password
        user.save()

        return user

    # =========================
    # UPDATE USER (SAFE FIX)
    # =========================
    def update(self, instance, validated_data):

        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance