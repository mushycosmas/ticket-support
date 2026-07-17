# apps/users/views/user_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.tickets.models import Ticket

from ..models import Team
from ..serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserTicketSerializer,
    ChangePasswordSerializer,
    TeamSerializer,
)

from .mixins import (
    UserViewSetPermissions,
    TicketStatsMixin,
    UserQuerySetMixin
)

from .base import BaseViewSetMixin


User = get_user_model()


class UserViewSet(
    UserViewSetPermissions,
    UserQuerySetMixin,
    TicketStatsMixin,
    BaseViewSetMixin,
    viewsets.ModelViewSet
):
    """
    User Management ViewSet with role-based access control.
    Supports:
    - Admin: Full access to all users
    - Team Lead: Access to users in their teams
    - Agent/Support: Access only to themselves
    """

    permission_classes = [IsAuthenticated]
    queryset = User.objects.all().order_by("-date_joined")

    # ==================================================
    # SERIALIZER
    # ==================================================

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer

        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer

        if self.action == "tickets":
            return UserTicketSerializer

        if self.action == "change_password":
            return ChangePasswordSerializer

        return UserSerializer

    # ==================================================
    # ROLE HELPERS
    # ==================================================

    def get_role(self, user):
        """Get user role from various possible sources."""
        if not user:
            return None

        if user.is_superuser:
            return "ADMIN"

        if hasattr(user, "role") and user.role:
            if hasattr(user.role, "name"):
                return user.role.name.upper()
            return str(user.role).upper()

        if hasattr(user, "role_name") and user.role_name:
            return user.role_name.upper()

        return None

    def is_admin(self, user):
        return self.get_role(user) == "ADMIN"

    def is_team_lead(self, user):
        return self.get_role(user) == "TEAM_LEAD"

    # ==================================================
    # PERMISSION CHECKS
    # ==================================================

    def has_permission(self, user, permission_codename):
        """Check if user has a specific permission."""
        if user.is_superuser:
            return True

        if self.is_admin(user):
            return True

        if hasattr(user, 'role') and user.role:
            return user.role.permissions.filter(codename=permission_codename).exists()

        return False

    def can_create_user(self, user):
        """Check if user can create new users."""
        return self.has_permission(user, 'add_user')

    def can_edit_user(self, user):
        """Check if user can edit users."""
        return self.has_permission(user, 'change_user')

    def can_delete_user(self, user):
        """Check if user can delete users."""
        return self.has_permission(user, 'delete_user')

    def can_view_user(self, user):
        """Check if user can view users."""
        return self.has_permission(user, 'view_user')

    # ==================================================
    # GET TEAM LEAD TEAMS
    # ==================================================

    def get_lead_team_ids(self, user):
        """
        Get teams managed by Team Lead.

        Supports:
        1. Team.lead ForeignKey
        2. User teams ManyToMany
        """
        team_ids = []

        # Method 1: Team lead field
        team_ids.extend(
            Team.objects.filter(lead=user).values_list("id", flat=True)
        )

        # Method 2: ManyToMany user teams
        if self.is_team_lead(user):
            team_ids.extend(user.teams.values_list("id", flat=True))

        return list(set(team_ids))

    # ==================================================
    # USER QUERYSET
    # ==================================================

    def get_queryset(self):
        """
        Filter users based on role:
        - ADMIN: All users
        - TEAM_LEAD: Users in their teams
        - AGENT/SUPPORT: Only themselves
        """
        user = self.request.user
        role = self.get_role(user)

        # ADMIN - See all users
        if role == "ADMIN" or user.is_superuser:
            return User.objects.all().order_by("-date_joined")

        # TEAM LEAD - See users in their teams
        if role == "TEAM_LEAD":
            team_ids = self.get_lead_team_ids(user)
            return User.objects.filter(
                teams__id__in=team_ids
            ).distinct().order_by("-date_joined")

        # AGENT / SUPPORT - See only themselves
        if role in ["AGENT", "SUPPORT"]:
            return User.objects.filter(id=user.id)

        return User.objects.none()

    # ==================================================
    # ACCESS CHECK
    # ==================================================

    def can_access_user(self, request_user, target_user):
        """Check if a user can access another user's data."""
        if self.is_admin(request_user) or request_user.is_superuser:
            return True

        if request_user.id == target_user.id:
            return True

        if self.is_team_lead(request_user):
            team_ids = self.get_lead_team_ids(request_user)
            return target_user.teams.filter(id__in=team_ids).exists()

        return False

    # ==================================================
    # LIST USERS
    # ==================================================

    def list(self, request, *args, **kwargs):
        """List all users with optional search and filters."""
        queryset = self.get_queryset()

        # Search filter
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        # Role filter
        role = request.query_params.get("role")
        if role:
            queryset = queryset.filter(role__name=role)

        # Team filter
        team_id = request.query_params.get("team_id")
        if team_id:
            queryset = queryset.filter(teams__id=team_id)

        # Active filter
        is_active = request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    # ==================================================
    # RETRIEVE USER
    # ==================================================

    def retrieve(self, request, *args, **kwargs):
        """Get a single user with all details."""
        instance = self.get_object()

        if not self.can_access_user(request.user, instance):
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # ==================================================
    # CREATE USER (With Permission Check)
    # ==================================================

    def create(self, request, *args, **kwargs):
        """Create a new user.
        
        Allowed:
        - Admin: Can create users
        - Users with 'add_user' permission
        - Team Lead: Can create users (but only with AGENT/SUPPORT roles)
        """
        request_user = request.user

        # ✅ Check if user has permission to create users
        if not self.can_create_user(request_user):
            return Response(
                {"error": "You don't have permission to create users"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ✅ Team Lead can only create users with AGENT or SUPPORT roles
        if self.is_team_lead(request_user) and not self.is_admin(request_user):
            role_id = request.data.get('role_id')
            if role_id:
                from ..models import Role
                try:
                    role = Role.objects.get(id=role_id)
                    if role.name.upper() not in ['AGENT', 'SUPPORT']:
                        return Response(
                            {"error": "Team Leads can only create users with AGENT or SUPPORT roles"},
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Role.DoesNotExist:
                    pass

        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    # ==================================================
    # UPDATE USER
    # ==================================================

    def update(self, request, *args, **kwargs):
        """Update a user.
        
        Allowed:
        - Admin: Can update any user
        - Team Lead: Can update users in their teams
        - Users with 'change_user' permission
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        request_user = request.user

        # ✅ Check if user has permission to edit users
        if not self.can_edit_user(request_user):
            return Response(
                {"error": "You don't have permission to edit users"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ✅ Check if user can access this specific user
        if not self.can_access_user(request_user, instance):
            return Response(
                {"error": "You don't have permission to edit this user"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ✅ Prevent non-admins from changing roles
        if not self.is_admin(request_user) and not request_user.is_superuser:
            if 'role' in request.data or 'role_id' in request.data:
                return Response(
                    {"error": "Only administrators can change user roles"},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = UserUpdateSerializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(UserSerializer(user).data)

    # ==================================================
    # DELETE USER
    # ==================================================

    def destroy(self, request, *args, **kwargs):
        """Delete a user.
        
        Allowed:
        - Admin: Can delete any user
        - Users with 'delete_user' permission
        """
        user = self.get_object()
        request_user = request.user

        # ✅ Check if user has permission to delete users
        if not self.can_delete_user(request_user):
            return Response(
                {"error": "You don't have permission to delete users"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ✅ Check if user can access this specific user
        if not self.can_access_user(request_user, user):
            return Response(
                {"error": "You don't have permission to delete this user"},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.id == request_user.id:
            return Response(
                {"error": "You cannot delete your own account"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user has assigned tickets
        if Ticket.objects.filter(assigned_to=user).exists():
            return Response(
                {"error": "Cannot delete user with assigned tickets. Reassign tickets first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.delete()
        return Response(
            {"message": "User deleted successfully"},
            status=status.HTTP_200_OK
        )

    # ==================================================
    # CURRENT USER
    # ==================================================

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """Get current authenticated user's information."""
        serializer = UserSerializer(request.user)
        data = serializer.data
        data['permissions'] = self._get_user_permissions(request.user)
        return Response(data)

    def _get_user_permissions(self, user):
        """Get all permissions for a user."""
        if user.is_superuser:
            return ["*"]

        permissions = []
        if hasattr(user, 'role') and user.role:
            permissions = list(user.role.permissions.values_list("codename", flat=True))

        return permissions

    # ==================================================
    # TEAM MEMBERS FOR LEAD
    # ==================================================

    @action(detail=False, methods=["get"], url_path="my_team_members")
    def my_team_members(self, request):
        """Get all members of teams where the current user is a team lead."""
        if not self.is_team_lead(request.user):
            return Response(
                {"error": "Only team leads can view team members"},
                status=status.HTTP_403_FORBIDDEN
            )

        team_ids = self.get_lead_team_ids(request.user)

        if not team_ids:
            return Response(
                {"message": "You are not a lead of any team", "results": []},
                status=status.HTTP_200_OK
            )

        members = User.objects.filter(teams__id__in=team_ids).distinct()

        return Response({
            "count": members.count(),
            "results": UserSerializer(members, many=True).data
        })

    # ==================================================
    # MY LEADING TEAMS
    # ==================================================

    @action(detail=False, methods=["get"], url_path="my_leading_teams")
    def my_leading_teams(self, request):
        """Get all teams where the current user is a team lead."""
        if not self.is_team_lead(request.user):
            return Response(
                {"error": "Only team leads can view their leading teams"},
                status=status.HTTP_403_FORBIDDEN
            )

        leading_teams = Team.objects.filter(lead=request.user)

        return Response({
            "count": leading_teams.count(),
            "results": TeamSerializer(leading_teams, many=True).data
        })

    # ==================================================
    # USER TEAMS
    # ==================================================

    @action(detail=True, methods=["get"], url_path="teams")
    def teams(self, request, pk=None):
        """Get all teams a user belongs to."""
        user = self.get_object()

        if not self.can_access_user(request.user, user):
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(
            TeamSerializer(user.teams.all(), many=True).data
        )

    # ==================================================
    # USER TICKETS
    # ==================================================

    @action(detail=True, methods=["get"], url_path="tickets")
    def tickets(self, request, pk=None):
        """Get tickets assigned to a user."""
        user = self.get_object()

        if not self.can_access_user(request.user, user):
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        status_filter = request.query_params.get("status")
        priority_filter = request.query_params.get("priority")

        tickets = Ticket.objects.filter(assigned_to=user).order_by('-created_at')

        if status_filter:
            tickets = tickets.filter(status=status_filter.upper())

        if priority_filter:
            tickets = tickets.filter(priority=priority_filter.upper())

        serializer = UserTicketSerializer(tickets, many=True)

        return Response({
            "count": tickets.count(),
            "results": serializer.data
        })

    # ==================================================
    # USER STATS
    # ==================================================

    @action(detail=True, methods=["get"], url_path="stats")
    def stats(self, request, pk=None):
        """Get ticket statistics for a user."""
        user = self.get_object()

        if not self.can_access_user(request.user, user):
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        tickets = Ticket.objects.filter(assigned_to=user)

        return Response({
            "total_assigned": tickets.count(),
            "total_open": tickets.filter(status='OPEN').count(),
            "total_in_progress": tickets.filter(status='IN_PROGRESS').count(),
            "total_resolved": tickets.filter(status='RESOLVED').count(),
            "total_closed": tickets.filter(status='CLOSED').count(),
        })

    # ==================================================
    # RESET PASSWORD (Admin or Team Lead)
    # ==================================================

    @action(detail=True, methods=["post"], url_path="reset_password")
    def reset_password(self, request, pk=None):
        """Reset a user's password to default.
        
        Allowed:
        - Admin: Can reset any user's password
        - Team Lead: Can reset password for users in their teams
        """
        target_user = self.get_object()
        request_user = request.user

        # Check if user can reset password for this user
        if not self._can_reset_password(request_user, target_user):
            return Response(
                {"error": "You don't have permission to reset this user's password"},
                status=status.HTTP_403_FORBIDDEN
            )

        default_password = request.data.get("password", "support123")

        target_user.set_password(default_password)
        target_user.is_default_password = True
        target_user.last_password_change = timezone.now()
        target_user.save(update_fields=['password', 'is_default_password', 'last_password_change'])

        return Response({
            "message": "Password reset successfully",
            "username": target_user.username,
            "default_password": default_password
        }, status=status.HTTP_200_OK)

    def _can_reset_password(self, request_user, target_user):
        """Check if a user can reset another user's password."""
        # Superuser can reset anyone's password
        if request_user.is_superuser:
            return True

        # Admin can reset anyone's password
        if self.is_admin(request_user):
            return True

        # Team Lead can reset password for users in their teams
        if self.is_team_lead(request_user):
            team_ids = self.get_lead_team_ids(request_user)
            if target_user.teams.filter(id__in=team_ids).exists():
                return True

        return False

    # ==================================================
    # CHANGE PASSWORD (User self-service)
    # ==================================================

    @action(detail=False, methods=["post"], url_path="change_password")
    def change_password(self, request):
        """Change the current user's password."""
        user = request.user

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response(
                {"error": "old_password and new_password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(old_password):
            return Response(
                {"error": "Wrong old password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.is_default_password = False
        user.last_password_change = timezone.now()
        user.save()

        return Response({
            "message": "Password changed successfully"
        }, status=status.HTTP_200_OK)

    # ==================================================
    # UPDATE PROFILE (User self-service)
    # ==================================================

    @action(detail=False, methods=["patch"], url_path="update_profile")
    def update_profile(self, request):
        """Update the current user's profile."""
        user = request.user

        allowed_fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture']
        data = {k: v for k, v in request.data.items() if k in allowed_fields}

        serializer = UserUpdateSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(UserSerializer(user).data)

    # ==================================================
    # PERMISSIONS
    # ==================================================

    @action(detail=True, methods=["get"], url_path="permissions")
    def permissions(self, request, pk=None):
        """Get user permissions."""
        user = self.get_object()

        if not self.can_access_user(request.user, user):
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response({
            "permissions": self._get_user_permissions(user)
        })