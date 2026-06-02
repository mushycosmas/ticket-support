from rest_framework import serializers
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):

    # readable fields (instead of IDs)
    team_name = serializers.CharField(source="team.name", read_only=True)

    assigned_to_name = serializers.SerializerMethodField()

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.username
        return None

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "created_at",
            "channel",
            "customer_contact",
            "customer_name",
            "team_id",
            "assigned_to_id",

            # readable fields
            "team_name",
            "assigned_to_name",
        ]