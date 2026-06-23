# apps/users/views/auth_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.contrib.auth import authenticate
from django.db import connection

from rest_framework_simplejwt.tokens import RefreshToken


class LoginView(APIView):
    """
    JWT Login Endpoint
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
        # WITHOUT touching user.role
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
        print("===================================\n")

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": user_data,
            },
            status=status.HTTP_200_OK,
        )