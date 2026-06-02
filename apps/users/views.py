from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .models import User, Team
from .serializers import UserSerializer, TeamSerializer


# =========================
# USER MANAGEMENT
# =========================
class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.select_related('team').all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        team_id = self.request.query_params.get('team')
        role = self.request.query_params.get('role')

        if team_id:
            queryset = queryset.filter(team_id=team_id)

        if role:
            queryset = queryset.filter(role=role)

        return queryset

    # =========================
    # RESET PASSWORD ACTION
    # =========================
    @action(detail=True, methods=["post"])
    def reset_password(self, request, pk=None):

        user = self.get_object()

        user.set_password("support123")
        user.save()

        return Response({
            "message": "Password reset to support123"
        })


# =========================
# TEAM MANAGEMENT
# =========================
class TeamViewSet(viewsets.ModelViewSet):

    queryset = Team.objects.all()
    serializer_class = TeamSerializer


# =========================
# LOGIN API (JWT)
# =========================


class LoginView(APIView):

    permission_classes = [AllowAny]   # 🔥 THIS FIXES 401

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=401
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "team": user.team.id if user.team else None
            }
        })

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=400
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "team": user.team.id if user.team else None
            }
        })