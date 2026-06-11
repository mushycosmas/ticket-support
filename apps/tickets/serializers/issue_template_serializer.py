# apps/tickets/serializers/issue_template_serializer.py

from rest_framework import serializers

from apps.tickets.models.issue_template import IssueTemplate
from apps.channels.models import Channel


class IssueTemplateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    priority_name = serializers.CharField(
        source="suggested_priority.name",
        read_only=True
    )

    channels = serializers.PrimaryKeyRelatedField(
        queryset=Channel.objects.all(),
        many=True,
        required=False
    )

    channel_names = serializers.SerializerMethodField()

    class Meta:
        model = IssueTemplate
        fields = [
            "id",
            "name",
            "description",

            # Category
            "category",
            "category_name",

            # Priority
            "suggested_priority",
            "priority_name",

            # Channels
            "channels",
            "channel_names",

            # Other fields
            "steps_to_reproduce",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "category_name",
            "priority_name",
            "channel_names",
        ]

    def get_channel_names(self, obj):
        return [
            channel.name
            for channel in obj.channels.all()
        ]