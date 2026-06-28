from rest_framework import serializers
from .models import Channel
from apps.users.models import Team



class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name", "description"]


class ChannelSerializer(serializers.ModelSerializer):
   
    team = TeamSerializer(read_only=True)

  
    team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        source="team",
        write_only=True
    )

    class Meta:
        model = Channel
        fields = [
            "id",
            "name",
            "status",
            "team",
            "team_id",
            "created_at",
            "updated_at",
        ]