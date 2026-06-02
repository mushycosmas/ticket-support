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

    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user

        if not user or not user.is_authenticated:
            return User.objects.none()

        queryset = User.objects.select_related("team").all()

        # =========================
        # ADMIN → ALL USERS
        # =========================
        if user.role == "ADMIN":
            return queryset

        # =========================
        # TEAM LEAD → ONLY TEAM AGENTS
        # =========================
        if user.role == "TEAM_LEAD":
            return queryset.filter(
                team=user.team,
                role="AGENT"
            )

        # =========================
        # AGENT → ONLY SELF
        # =========================
        if user.role == "AGENT":
            return queryset.filter(id=user.id)

        return User.objects.none()

    # =========================
    # RESET PASSWORD
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
# LOGIN API (FIXED)
# =========================
class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
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
                "team_id": user.team.id if user.team else None
            }
        })