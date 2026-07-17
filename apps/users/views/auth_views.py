# apps/users/views/auth_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from django.contrib.auth import authenticate
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import Team


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_role_data(user):
    """
    Get role and permissions for a user.
    
    Returns:
        tuple: (role_name, permissions_list)
    """
    role_name = None
    permissions = []

    if user.is_superuser:
        permissions = ["*"]
        return "SUPERUSER", permissions

    if user.role:
        role_name = user.role.name
        permissions = list(
            user.role.permissions.values_list(
                "codename",
                flat=True
            )
        )

    return role_name, permissions


def get_team_data(user):
    """
    Get user's teams and teams where user is a team lead.
    
    A user is a team lead if:
    1. They have the global TEAM_LEAD role
    2. They are a member of the team
    
    Returns:
        dict: {
            "team_ids": [1, 2],
            "team_names": ["Security", "Database"],
            "leading_team_ids": [1, 2],
            "leading_team_names": ["Security", "Database"],
            "is_team_lead_anywhere": True
        }
    """
    # Get all teams the user belongs to (ManyToMany)
    teams = user.teams.all()
    
    team_ids = list(teams.values_list("id", flat=True))
    team_names = list(teams.values_list("name", flat=True))
    
    # Get teams where user is a team lead
    # User is a team lead if they have TEAM_LEAD role globally
    # AND they are a member of the team (which they already are)
    leading_team_ids = []
    leading_team_names = []
    
    # Check if user has the global TEAM_LEAD role
    is_global_team_lead = (
        user.role and 
        user.role.name and 
        user.role.name.upper() == 'TEAM_LEAD'
    )
    
    if is_global_team_lead:
        # User is a team lead for all teams they belong to
        leading_team_ids = team_ids
        leading_team_names = team_names
    
    return {
        "team_ids": team_ids,
        "team_names": team_names,
        "leading_team_ids": leading_team_ids,
        "leading_team_names": leading_team_names,
        "is_team_lead_anywhere": len(leading_team_ids) > 0,
    }


def build_user_data(user):
    """
    Build complete user data response for login and profile.
    """
    role_name, permissions = get_role_data(user)
    team_data = get_team_data(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.get_full_name() or user.username,
        "rank": user.rank,
        "profile_picture": user.profile_picture.url if user.profile_picture else None,
        "role": role_name,
        "role_id": user.role.id if user.role else None,
        # Team data
        "team_ids": team_data["team_ids"],
        "team_names": team_data["team_names"],
        "leading_team_ids": team_data["leading_team_ids"],
        "leading_team_names": team_data["leading_team_names"],
        "is_team_lead_anywhere": team_data["is_team_lead_anywhere"],
        # Status
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "is_default_password": user.is_default_password,
        "needs_password_change": user.is_default_password,
        # Dates
        "last_login": user.last_login,
        "date_joined": user.date_joined,
        # Permissions
        "permissions": permissions,
    }


# ============================================================
# LOGIN VIEW
# ============================================================

class LoginView(APIView):
    """
    Login endpoint - Authenticates user and returns JWT tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"detail": "Account disabled"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        user.refresh_from_db()

        # Build user data
        user_data = build_user_data(user)

        # Debug log
        print("\n========== LOGIN ==========")
        print(f"USER: {user.username}")
        print(f"ROLE: {user_data['role']}")
        print(f"TEAMS: {user_data['team_names']}")
        print(f"LEADING: {user_data['leading_team_names']}")
        print("===========================\n")

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": user_data,
                "needs_password_change": user.is_default_password
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# ME VIEW (Current User)
# ============================================================

class MeView(APIView):
    """
    Get current authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user.refresh_from_db()

        return Response(
            {"user": build_user_data(user)},
            status=status.HTTP_200_OK
        )


# ============================================================
# CHANGE PASSWORD
# ============================================================

class ChangePasswordView(APIView):
    """
    Change current user's password.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        old_password = (
            request.data.get("old_password") or
            request.data.get("current_password")
        )

        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        # Validate old password
        if not user.check_password(old_password):
            return Response(
                {"error": "Current password incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate new password
        if new_password != confirm_password:
            return Response(
                {"error": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set new password
        user.set_password(new_password)
        user.is_default_password = False
        user.last_password_change = timezone.now()
        user.save()

        return Response(
            {
                "message": "Password changed successfully",
                "needs_password_change": False
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# LOGOUT VIEW
# ============================================================

class LogoutView(APIView):
    """
    Logout endpoint - Blacklists the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("refresh")

        if token:
            refresh = RefreshToken(token)
            refresh.blacklist()

        return Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )


# ============================================================
# REFRESH TOKEN VIEW
# ============================================================

class RefreshTokenView(APIView):
    """
    Refresh access token using refresh token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            return Response(
                {
                    "access": access_token,
                    "refresh": str(refresh)
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================
# VERIFY TOKEN VIEW
# ============================================================

class VerifyTokenView(APIView):
    """
    Verify if the current token is valid.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user.refresh_from_db()

        return Response(
            {
                "valid": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.get_full_name() or user.username,
                }
            },
            status=status.HTTP_200_OK
        )