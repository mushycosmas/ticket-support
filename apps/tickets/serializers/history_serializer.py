from rest_framework import serializers
from apps.tickets.models import TicketHistory


class TicketHistorySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = TicketHistory
        fields = [
            "id",
            "action",
            "comment",
            "old_status",
            "new_status",
            "created_by",
            "created_by_name",
            "created_at",
        ]