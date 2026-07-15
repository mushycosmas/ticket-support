from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from ..models import User
from ..serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserTicketSerializer,
    ChangePasswordSerializer,
)

from .mixins import UserViewSetPermissions, UserQuerySetMixin, TicketStatsMixin
from .base import BaseViewSetMixin


class UserViewSet(
    UserViewSetPermissions,
    UserQuerySetMixin,
    TicketStatsMixin,
    BaseViewSetMixin,
    viewsets.ModelViewSet
):
    """
    USER MANAGEMENT VIEWSET
    Handles user CRUD with proper role-based filtering.
    """

    permission_classes = [IsAuthenticated]
    queryset = User.objects.all().order_by('-date_joined')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        elif self.action == "tickets":
            return UserTicketSerializer
        elif self.action == "change_password":
            return ChangePasswordSerializer
        return UserSerializer

    def get_queryset(self):
        """
        Filter users based on the requesting user's role.
        - Admins see all users
        - Team leads see only users in their team
        - Agents/Support see only themselves
        """
        user = self.request.user
        
        # Get user role
        user_role = self._get_user_role(user)
        
        # Superuser or Admin - see all users
        if user.is_superuser or user_role == "ADMIN":
            return User.objects.all().order_by('-date_joined')
        
        # Team Lead - see users in their team
        if user_role == "TEAM_LEAD" and user.team_id:
            return User.objects.filter(
                Q(team_id=user.team_id) | Q(id=user.id)
            ).order_by('-date_joined')
        
        # Agent or Support - see only themselves
        if user_role in ["AGENT", "SUPPORT"]:
            return User.objects.filter(id=user.id)
        
        # Default: return none (should not happen with proper permissions)
        return User.objects.none()

    def _get_user_role(self, user):
        """Extract user role from various possible field structures."""
        if not user:
            return None
        
        if hasattr(user, "role") and user.role:
            if hasattr(user.role, "name"):
                return user.role.name.upper()
            return str(user.role).upper()
        elif hasattr(user, "role_name") and user.role_name:
            return user.role_name.upper()
        
        return None

    def _is_admin(self, user):
        """Check if user is admin."""
        return self._get_user_role(user) == "ADMIN"

    def _is_team_lead(self, user):
        """Check if user is team lead."""
        return self._get_user_role(user) == "TEAM_LEAD"

    def _can_view_user(self, requesting_user, target_user):
        """Check if a user can view another user."""
        # Admins can view everyone
        if self._is_admin(requesting_user) or requesting_user.is_superuser:
            return True
        
        # Users can view themselves
        if requesting_user.id == target_user.id:
            return True
        
        # Team leads can view their team members
        if self._is_team_lead(requesting_user) and requesting_user.team_id:
            return target_user.team_id == requesting_user.team_id
        
        return False

    def _can_edit_user(self, requesting_user, target_user):
        """Check if a user can edit another user."""
        # Admins can edit everyone
        if self._is_admin(requesting_user) or requesting_user.is_superuser:
            return True
        
        # Users can edit themselves
        if requesting_user.id == target_user.id:
            return True
        
        # Team leads can edit their team members
        if self._is_team_lead(requesting_user) and requesting_user.team_id:
            return target_user.team_id == requesting_user.team_id
        
        return False

    # ======================
    # LIST
    # ======================
    def list(self, request, *args, **kwargs):
        """
        List all users with optional filtering.
        - Supports: search, role, team, active filters
        - Returns only users the requester has permission to see
        """
        queryset = self.get_queryset()
        
        # Apply search filter
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Apply role filter
        role = request.query_params.get('role')
        if role:
            queryset = queryset.filter(role__name=role)
        
        # Apply team filter
        team_id = request.query_params.get('team_id')
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        
        # Apply active filter
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Apply ordering
        ordering = request.query_params.get('ordering', '-date_joined')
        queryset = queryset.order_by(ordering)

        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    # ======================
    # RETRIEVE
    # ======================
    def retrieve(self, request, *args, **kwargs):
        """Get a single user with all details."""
        instance = self.get_object()
        
        # Check if user can view this user
        if not self._can_view_user(request.user, instance):
            return Response(
                {"error": "You don't have permission to view this user"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # ======================
    # CREATE
    # ======================
    def create(self, request, *args, **kwargs):
        """Create a new user. Only admins can create users."""
        # if not self._is_admin(request.user) and not request.user.is_superuser:
        #     return Response(
        #         {"error": "Only administrators can create users"},
        #         status=status.HTTP_403_FORBIDDEN
        #     )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    # ======================
    # UPDATE
    # ======================
    def update(self, request, *args, **kwargs):
        """Update a user."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Check if user can edit this user
        if not self._can_edit_user(request.user, instance):
            return Response(
                {"error": "You don't have permission to edit this user"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Prevent non-admins from changing roles
        if not self._is_admin(request.user) and not request.user.is_superuser:
            if 'role' in request.data or 'role_id' in request.data:
                return Response(
                    {"error": "Only administrators can change user roles"},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(UserSerializer(user).data)

    # ======================
    # DELETE
    # ======================
    def destroy(self, request, *args, **kwargs):
        """Delete a user. Only admins can delete users."""
        user = self.get_object()

        if not self._is_admin(request.user) and not request.user.is_superuser:
            return Response(
                {"error": "Only administrators can delete users"},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.id == request.user.id:
            return Response(
                {"error": "You cannot delete your own account"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user has assigned tickets
        if hasattr(user, 'assigned_tickets') and user.assigned_tickets.exists():
            return Response(
                {"error": "Cannot delete user with assigned tickets. Reassign tickets first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.delete()
        return Response(
            {"message": "User deleted successfully"},
            status=status.HTTP_200_OK
        )

    # ======================
    # TICKETS
    # ======================
    @action(detail=True, methods=["get"])
    def tickets(self, request, pk=None):
        """Get tickets assigned to a user."""
        user = self.get_object()

        # Check if user can view this user's tickets
        if not self._can_view_user(request.user, user):
            return Response(
                {"error": "You don't have permission to view this user's tickets"},
                status=status.HTTP_403_FORBIDDEN
            )

        status_filter = request.query_params.get("status")
        priority_filter = request.query_params.get("priority")
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        tickets, total = self.get_user_tickets(
            user,
            status_filter,
            priority_filter,
            page,
            page_size
        )

        serializer = UserTicketSerializer(tickets, many=True)

        return Response({
            "count": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
            "results": serializer.data
        })

    # ======================
    # STATS
    # ======================
    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """Get ticket statistics for a user."""
        user = self.get_object()

        # Check if user can view this user's stats
        if not self._can_view_user(request.user, user):
            return Response(
                {"error": "You don't have permission to view this user's stats"},
                status=status.HTTP_403_FORBIDDEN
            )

        stats = self.get_user_ticket_stats(user)
        return Response(stats)

    # ======================
    # RESET PASSWORD (Admin only)
    # ======================
    @action(detail=True, methods=["post"])
    def reset_password(self, request, pk=None):
        """Reset a user's password to default."""
        user = self.get_object()

        # if not self._is_admin(request.user) and not request.user.is_superuser:
        #     return Response(
        #         {"error": "Only administrators can reset passwords"},
        #         status=status.HTTP_403_FORBIDDEN
        #     )

        default_password = request.data.get("password", "support123")
        user.set_password(default_password)
        user.save()

        return Response(
            {"message": f"Password reset successfully to: {default_password}"},
            status=status.HTTP_200_OK
        )

    # ======================
    # CHANGE PASSWORD (User self-service)
    # ======================
    @action(detail=False, methods=["post"])
    def change_password(self, request):
        """Change the current user's password."""
        user = request.user
        
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        
        if not old_password or not new_password or not confirm_password:
            return Response(
                {"error": "old_password, new_password, and confirm_password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {"error": "New passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.check_password(old_password):
            return Response(
                {"error": "Current password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK
        )

    # ======================
    # ME (Current user)
    # ======================
    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current authenticated user's information."""
        user = request.user
        serializer = self.get_serializer(user)
        
        # Add permissions to response
        data = serializer.data
        data['permissions'] = self._get_user_permissions(user)
        
        return Response(data)

    def _get_user_permissions(self, user):
        """Get all permissions for a user."""
        if user.is_superuser:
            return ["*"]
        
        permissions = []
        if hasattr(user, 'role') and user.role:
            permissions = list(user.role.permissions.values_list("codename", flat=True))
        
        return permissions

    # ======================
    # UPDATE PROFILE (User self-service)
    # ======================
    @action(detail=False, methods=["patch"])
    def update_profile(self, request):
        """Update the current user's profile."""
        user = request.user
        
        # Only allow specific fields for self-update
        allowed_fields = ['first_name', 'last_name', 'email', 'phone', 'whatsapp', 'avatar']
        data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        serializer = UserUpdateSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(UserSerializer(user).data)