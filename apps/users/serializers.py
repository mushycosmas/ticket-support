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

    # ✅ FIX: not required anymore
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )

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
            'team_id',
            'team_name',
            'is_active',
            'date_joined',
        ]

        read_only_fields = ['id', 'date_joined']

    # =========================
    # CREATE USER
    # =========================
    def create(self, validated_data):

        password = validated_data.pop('password', None)

        if not password:
            password = "support123"

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user

    # =========================
    # UPDATE USER
    # =========================
    def update(self, instance, validated_data):

        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # only update password if provided
        if password:
            instance.set_password(password)

        instance.save()
        return instance