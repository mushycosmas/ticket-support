# apps/users/views/auth_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from django.contrib.auth import authenticate
from django.db import connection
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken


# ============================================================
# LOGIN VIEW
# ============================================================
class LoginView(APIView):
    """
    JWT Login Endpoint
    Returns user data with permissions, team info, and password change status.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        # -----------------------------
        # Validate Input
        # -----------------------------
        if not username or not password:
            return Response(
                {"detail": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------
        # Authenticate User
        # -----------------------------
        user = authenticate(
            username=username,
            password=password,
        )

        if user is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "User account is disabled"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Refresh from database
        user.refresh_from_db()

        # -----------------------------
        # Get Role Information
        # -----------------------------
        role_name = None
        permissions = []

        if user.role_id:
            with connection.cursor() as cursor:

                # Get role name
                cursor.execute(
                    """
                    SELECT name
                    FROM roles_role
                    WHERE id = %s
                    """,
                    [user.role_id],
                )

                role_row = cursor.fetchone()

                if role_row:
                    role_name = role_row[0]

                # Get permissions
                cursor.execute(
                    """
                    SELECT p.codename
                    FROM auth_permission p
                    INNER JOIN roles_role_permissions rp
                        ON p.id = rp.permission_id
                    WHERE rp.role_id = %s
                    """,
                    [user.role_id],
                )

                permissions = [
                    row[0]
                    for row in cursor.fetchall()
                ]

        # -----------------------------
        # Team Name
        # -----------------------------
        team_name = None

        if user.team_id:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT name
                    FROM users_team
                    WHERE id = %s
                    """,
                    [user.team_id],
                )

                team_row = cursor.fetchone()

                if team_row:
                    team_name = team_row[0]

        # -----------------------------
        # Superuser Override
        # -----------------------------
        if user.is_superuser:
            permissions = ["*"]

        # -----------------------------
        # ✅ Check if user needs to change password
        # -----------------------------
        needs_password_change = user.is_default_password

        # -----------------------------
        # JWT Tokens
        # -----------------------------
        refresh = RefreshToken.for_user(user)

        # -----------------------------
        # User Data
        # -----------------------------
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.get_full_name() or user.username,
            "rank": user.rank,
            "role": role_name,
            "role_id": user.role_id,
            "team_id": user.team_id,
            "team_name": team_name,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "permissions": permissions,
            "is_default_password": needs_password_change,
            "needs_password_change": needs_password_change,
        }

        # -----------------------------
        # Debug Logs
        # -----------------------------
        print("\n========== LOGIN SUCCESS ==========")
        print("Username:", user.username)
        print("User ID:", user.id)
        print("Role ID:", user.role_id)
        print("Role Name:", role_name)
        print("Permissions:", len(permissions))
        print("Needs Password Change:", needs_password_change)
        print("===================================\n")

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": user_data,
                "needs_password_change": needs_password_change,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# CHANGE PASSWORD VIEW
# ============================================================
class ChangePasswordView(APIView):
    """
    Change password endpoint.
    Requires authentication.
    Accepts: current_password, new_password, confirm_password
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # ✅ Support both field names for flexibility
        current_password = request.data.get("current_password") or request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        # -----------------------------
        # Validate Input
        # -----------------------------
        if not current_password:
            return Response(
                {"current_password": ["Current password is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not new_password:
            return Response(
                {"new_password": ["New password is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not confirm_password:
            return Response(
                {"confirm_password": ["Please confirm your new password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {"confirm_password": ["Passwords do not match."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_password) < 6:
            return Response(
                {"new_password": ["Password must be at least 6 characters long."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prevent reusing default password
        if new_password.lower() == "support123":
            return Response(
                {"new_password": ["You cannot reuse the default password. Please choose a different password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------
        # Verify Current Password
        # -----------------------------
        if not user.check_password(current_password):
            return Response(
                {"current_password": ["Current password is incorrect."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------
        # Set New Password
        # -----------------------------
        user.set_password(new_password)
        user.save()

        # Refresh user data
        user.refresh_from_db()

        print(f"\n========== PASSWORD CHANGED ==========")
        print(f"User: {user.username} (ID: {user.id})")
        print(f"Password changed at: {user.last_password_change}")
        print(f"Is default password: {user.is_default_password}")
        print("=======================================\n")

        return Response(
            {
                "message": "Password changed successfully",
                "needs_password_change": False,
                "is_default_password": False,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# LOGOUT VIEW
# ============================================================
class LogoutView(APIView):
    """
    Logout endpoint - blacklist the refresh token.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ============================================================
# REFRESH TOKEN VIEW
# ============================================================
class RefreshTokenView(APIView):
    """
    Refresh access token endpoint.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            return Response(
                {"access": access_token},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


# ============================================================
# CURRENT USER VIEW
# ============================================================
class MeView(APIView):
    """
    Get current authenticated user's information.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user.refresh_from_db()

        # Get role and permissions
        role_name = None
        permissions = []

        if user.role_id:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT name
                    FROM roles_role
                    WHERE id = %s
                    """,
                    [user.role_id],
                )
                role_row = cursor.fetchone()
                if role_row:
                    role_name = role_row[0]

                cursor.execute(
                    """
                    SELECT p.codename
                    FROM auth_permission p
                    INNER JOIN roles_role_permissions rp
                        ON p.id = rp.permission_id
                    WHERE rp.role_id = %s
                    """,
                    [user.role_id],
                )
                permissions = [row[0] for row in cursor.fetchall()]

        if user.is_superuser:
            permissions = ["*"]

        # Get team name
        team_name = None
        if user.team_id:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT name
                    FROM users_team
                    WHERE id = %s
                    """,
                    [user.team_id],
                )
                team_row = cursor.fetchone()
                if team_row:
                    team_name = team_row[0]

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.get_full_name() or user.username,
            "rank": user.rank,
            "role": role_name,
            "role_id": user.role_id,
            "team_id": user.team_id,
            "team_name": team_name,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "permissions": permissions,
            "is_default_password": user.is_default_password,
            "needs_password_change": user.is_default_password,
            "last_login": user.last_login,
            "date_joined": user.date_joined,
        }

        return Response(
            {"user": user_data},
            status=status.HTTP_200_OK,
        )


# ============================================================
# CHECK DEFAULT PASSWORD STATUS
# ============================================================
class CheckDefaultPasswordView(APIView):
    """
    Check if current user is using the default password.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user.refresh_from_db()

        return Response(
            {
                "is_default_password": user.is_default_password,
                "needs_password_change": user.is_default_password,
                "last_password_change": user.last_password_change,
            },
            status=status.HTTP_200_OK,
        )