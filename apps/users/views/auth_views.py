# apps/users/views/auth_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import connection


class LoginView(APIView):
    """Login endpoint for JWT authentication"""

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
                {"detail": "User account is disabled"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ✅ Force refresh from database
        user.refresh_from_db()
        
        # ✅ Get permissions with a direct query
        permissions = []
        
        if user.role_id:
            # Direct SQL query to get permissions (bypasses ORM issues)
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT p.codename 
                    FROM auth_permission p
                    INNER JOIN roles_role_permissions rp ON p.id = rp.permission_id
                    WHERE rp.role_id = %s
                """, [user.role_id])
                rows = cursor.fetchall()
                permissions = [row[0] for row in rows]
            
            print(f"Direct SQL query found {len(permissions)} permissions")  # Debug
            
        # Alternative: Use Django ORM with explicit query
        if not permissions and user.role:
            # Force evaluate the queryset
            permissions = list(user.role.permissions.values_list("codename", flat=True))
            print(f"ORM query found {len(permissions)} permissions")  # Debug

        # Superuser gets all permissions
        if user.is_superuser:
            permissions = ["*"]

        refresh = RefreshToken.for_user(user)

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.get_full_name() or user.username,
            "rank": getattr(user, 'rank', None),
            "role": user.role.name if user.role else None,
            "role_id": user.role_id,
            "team_id": user.team_id,
            "team_name": user.team.name if user.team else None,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "permissions": permissions,  # Should now have permissions
        }

        # Debug print
        print(f"=== LOGIN RESPONSE ===")
        print(f"User: {user.username}")
        print(f"Role ID: {user.role_id}")
        print(f"Permissions count: {len(permissions)}")
        print(f"First 5 permissions: {permissions[:5] if permissions else 'None'}")
        print(f"=====================")

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user_data
        })