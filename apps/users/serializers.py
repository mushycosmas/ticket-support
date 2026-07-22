from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from apps.roles.models import Role
from apps.tickets.models import Ticket
from .models import Team


User = get_user_model()


# ============================================================
# 👤 USER SERIALIZER (READ)
# ============================================================
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    team_names = serializers.SerializerMethodField()
    team_ids = serializers.SerializerMethodField()
    leading_team_ids = serializers.SerializerMethodField()
    leading_team_names = serializers.SerializerMethodField()
    is_team_lead_anywhere = serializers.SerializerMethodField()
    is_global_team_lead = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "rank",
            "phone",
            "profile_picture",
            "role",
            "role_name",
            "team_names",
            "team_ids",
            "leading_team_ids",
            "leading_team_names",
            "is_team_lead_anywhere",
            "is_global_team_lead",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_default_password",
            "last_login",
            "date_joined",
            "permissions",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_team_names(self, obj):
        """Get list of team names the user belongs to"""
        return list(obj.teams.values_list('name', flat=True))

    def get_team_ids(self, obj):
        """Get list of team IDs the user belongs to"""
        return list(obj.teams.values_list('id', flat=True))

    def get_leading_team_ids(self, obj):
        """
        Get teams where user is a team lead.
        Based on: User has TEAM_LEAD role AND is a member of the team.
        """
        # ✅ Check if user has the global TEAM_LEAD role directly
        is_global_team_lead = obj.role and obj.role.name and obj.role.name.upper() == 'TEAM_LEAD'
        
        if not is_global_team_lead:
            return []
        
        # User is a team lead for all teams they belong to
        return list(obj.teams.values_list('id', flat=True))

    def get_leading_team_names(self, obj):
        """Get team names where user is a team lead."""
        # ✅ Check if user has the global TEAM_LEAD role directly
        is_global_team_lead = obj.role and obj.role.name and obj.role.name.upper() == 'TEAM_LEAD'
        
        if not is_global_team_lead:
            return []
        
        return list(obj.teams.values_list('name', flat=True))

    def get_is_team_lead_anywhere(self, obj):
        """Check if user is a team lead in any team."""
        # ✅ Check if user has the global TEAM_LEAD role directly
        is_global_team_lead = obj.role and obj.role.name and obj.role.name.upper() == 'TEAM_LEAD'
        return is_global_team_lead and obj.teams.exists()

    def get_is_global_team_lead(self, obj):
        """Check if user has the global TEAM_LEAD role."""
        return obj.role and obj.role.name and obj.role.name.upper() == 'TEAM_LEAD'

    def get_permissions(self, obj):
        if obj.is_superuser:
            return ["*"]

        if obj.role:
            return list(obj.role.permissions.values_list("codename", flat=True))

        return []

    def get_role_name(self, obj):
        return getattr(obj.role, "name", None)


# ============================================================
# 👤 CHANGE PASSWORD SERIALIZER
# ============================================================
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "New passwords do not match"}
            )
        return data


# ============================================================
# 👤 CREATE USER SERIALIZER
# ============================================================
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    role_id = serializers.PrimaryKeyRelatedField(
        source="role",
        queryset=Role.objects.all(),
        required=False,
        allow_null=True
    )

    teams = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        many=True,
        required=False,
        help_text="List of team IDs to assign the user to"
    )

    # Support single team for backward compatibility
    team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
        help_text="Single team ID (for backward compatibility)"
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "rank",
            "profile_picture",
            "role_id",
            "teams",
            "team",
        ]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match"}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        
        # Handle both team and teams
        teams = validated_data.pop("teams", [])
        team = validated_data.pop("team", None)
        
        # If team is provided and teams is empty, use it
        if team is not None and not teams:
            teams = [team]

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if teams:
            user.teams.set(teams)

        return user


# ============================================================
# 👤 UPDATE USER SERIALIZER
# ============================================================
class UserUpdateSerializer(serializers.ModelSerializer):
    role_id = serializers.PrimaryKeyRelatedField(
        source="role",
        queryset=Role.objects.all(),
        required=False,
        allow_null=True
    )

    teams = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        many=True,
        required=False,
        help_text="List of team IDs to assign the user to"
    )

    # Support single team for backward compatibility
    team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
        help_text="Single team ID (for backward compatibility)"
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "role_id",
            "rank",
            "profile_picture",
            "teams",
            "team",
            "is_active",
        ]

    def update(self, instance, validated_data):
        # Handle both team and teams
        teams = validated_data.pop("teams", None)
        team = validated_data.pop("team", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # If team is provided, add it to teams
        if team is not None:
            if teams is None:
                teams = [team]
            else:
                if not isinstance(teams, list):
                    teams = list(teams)
                if team not in teams:
                    teams.append(team)

        if teams is not None:
            instance.teams.set(teams)

        return instance


# ============================================================
# 🎟 USER TICKETS SERIALIZER
# ============================================================
class UserTicketSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_number",
            "title",
            "description",
            "status",
            "priority",
            "created_at",
            "updated_at",
            "resolved_at",
            "customer_name",
            "assigned_to_name",
        ]

    def get_customer_name(self, obj):
        return obj.customer.full_name if obj.customer else None

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name() if obj.assigned_to else None


# ============================================================
# 📊 USER STATS SERIALIZER
# ============================================================
class UserStatsSerializer(serializers.Serializer):
    total_assigned = serializers.IntegerField()
    total_open = serializers.IntegerField()
    total_in_progress = serializers.IntegerField()
    total_resolved = serializers.IntegerField()
    total_closed = serializers.IntegerField()


# ============================================================
# 👥 TEAM SERIALIZER (Without lead_id)
# ============================================================
class TeamSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    lead_names = serializers.SerializerMethodField()
    lead_ids = serializers.SerializerMethodField()
    team_leads = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "description",
            "lead_names",
            "lead_ids",
            "team_leads",
            "member_count",
            "created_at",
            "updated_at",
        ]

    def get_member_count(self, obj):
        """Get total number of members in the team."""
        return obj.members.count()

    def get_lead_names(self, obj):
        """Get all team lead names as a comma-separated string."""
        leads = obj.members.filter(role__name='TEAM_LEAD')
        return ", ".join([lead.full_name or lead.username for lead in leads]) if leads.exists() else "-"

    def get_lead_ids(self, obj):
        """Get all team lead IDs."""
        leads = obj.members.filter(role__name='TEAM_LEAD')
        return list(leads.values_list('id', flat=True))

    def get_team_leads(self, obj):
        """Get detailed team lead information."""
        leads = obj.members.filter(role__name='TEAM_LEAD')
        return [
            {
                "id": lead.id,
                "username": lead.username,
                "full_name": lead.full_name or lead.username,
                "email": lead.email,
            }
            for lead in leads
        ]


# ============================================================
# 👥 TEAM CREATE SERIALIZER
# ============================================================
class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["name", "description"]

    def create(self, validated_data):
        team = Team.objects.create(**validated_data)
        
        # Auto-add creator as member
        user = self.context.get('request').user
        if user and user.is_authenticated:
            team.members.add(user)
        
        return team


# ============================================================
# 👥 TEAM UPDATE SERIALIZER
# ============================================================
class TeamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["name", "description"]


# ============================================================
# 👥 TEAM MEMBERS SERIALIZER
# ============================================================
class TeamMemberSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()
    team_names = serializers.SerializerMethodField()
    is_team_lead = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "rank",
            "profile_picture",
            "role",
            "role_name",
            "team_names",
            "is_team_lead",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_role_name(self, obj):
        return getattr(obj.role, "name", None)

    def get_team_names(self, obj):
        return list(obj.teams.values_list('name', flat=True))

    def get_is_team_lead(self, obj):
        """Check if user has TEAM_LEAD role."""
        return obj.role and obj.role.name and obj.role.name.upper() == 'TEAM_LEAD'


# ============================================================
# 👥 TEAM DETAIL SERIALIZER
# ============================================================
class TeamDetailSerializer(TeamSerializer):
    members = serializers.SerializerMethodField()

    class Meta(TeamSerializer.Meta):
        fields = TeamSerializer.Meta.fields + ['members']

    def get_members(self, obj):
        members = obj.members.all()
        return TeamMemberSerializer(members, many=True).data


# ============================================================
# 📋 USER TEAM ASSIGNMENT SERIALIZER
# ============================================================
class UserTeamAssignmentSerializer(serializers.Serializer):
    """
    Serializer for assigning a user to a team (using ManyToMany)
    """
    team_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    def validate_team_id(self, value):
        if not Team.objects.filter(id=value).exists():
            raise serializers.ValidationError("Team does not exist")
        return value

    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist")
        return value

    def validate(self, data):
        user = User.objects.get(id=data['user_id'])
        team = Team.objects.get(id=data['team_id'])
        
        if user.teams.filter(id=team.id).exists():
            raise serializers.ValidationError(
                "User is already a member of this team"
            )
        
        return data


# ============================================================
# 📋 USER TEAM ROLE UPDATE SERIALIZER
# ============================================================
class UserTeamRoleUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating a user's role in a team.
    """
    role = serializers.CharField(required=True)
    is_active = serializers.BooleanField(required=False)

    def validate_role(self, value):
        valid_roles = ['TEAM_LEAD', 'AGENT', 'SUPPORT', 'VIEWER']
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        return value


# ============================================================
# 📋 TEAM LEADS SERIALIZER
# ============================================================
class TeamLeadsSerializer(serializers.Serializer):
    """
    Serializer for managing team leads.
    """
    user_id = serializers.IntegerField(required=True)
    
    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist")
        return value
    
    def validate(self, data):
        user = User.objects.get(id=data['user_id'])
        
        # Check if user has global TEAM_LEAD role
        is_global_team_lead = user.role and user.role.name and user.role.name.upper() == 'TEAM_LEAD'
        if not is_global_team_lead:
            raise serializers.ValidationError(
                f"User {user.username} does not have the global TEAM_LEAD role"
            )
        
        return data


# ============================================================
# 📱 UPDATE PHONE SERIALIZER
# ============================================================
class UpdatePhoneSerializer(serializers.Serializer):
    """
    Serializer for updating user's phone number.
    Validates Tanzania phone number format.
    """
    phone = serializers.CharField(required=True, max_length=20)

    def validate_phone(self, value):
        """
        Validate phone number format:
        - Must start with 255
        - Must be exactly 12 digits
        - Remove all non-digit characters
        """
        import re
        cleaned = re.sub(r'\D', '', value)
        
        if not cleaned:
            raise serializers.ValidationError("Phone number is required")
        
        # Check if it starts with 255
        if not cleaned.startswith('255'):
            raise serializers.ValidationError(
                "Phone number must start with 255 (Tanzania country code)"
            )
        
        # Check length (must be exactly 12 digits)
        if len(cleaned) != 12:
            raise serializers.ValidationError(
                f"Phone number must be exactly 12 digits (current: {len(cleaned)})"
            )
        
        return cleaned

    def update(self, instance, validated_data):
        """Update user's phone number"""
        instance.phone = validated_data['phone']
        instance.save()
        return instance


# ============================================================
# 📱 USER PROFILE UPDATE SERIALIZER
# ============================================================
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile (phone, name, email)
    """
    class Meta:
        model = User
        fields = ['phone', 'first_name', 'last_name', 'email']
        extra_kwargs = {
            'phone': {'required': False, 'allow_blank': True, 'allow_null': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'email': {'required': False, 'allow_blank': True},
        }

    def validate_phone(self, value):
        """Validate phone number if provided"""
        if not value:
            return value
        
        import re
        cleaned = re.sub(r'\D', '', value)
        
        if not cleaned:
            return value
        
        if not cleaned.startswith('255'):
            raise serializers.ValidationError(
                "Phone number must start with 255 (Tanzania country code)"
            )
        
        if len(cleaned) != 12:
            raise serializers.ValidationError(
                f"Phone number must be exactly 12 digits (current: {len(cleaned)})"
            )
        
        return cleaned