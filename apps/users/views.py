from rest_framework import viewsets
from .models import User, Team
from .serializers import UserSerializer, TeamSerializer


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


# ✅ ADD THIS (THIS WAS MISSING)
class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer