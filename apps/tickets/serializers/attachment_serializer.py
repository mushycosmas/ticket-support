from rest_framework import serializers
from ..models.attachment import TicketAttachment

class TicketAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for ticket file attachments"""

    uploaded_by_name = serializers.CharField(
        source="uploaded_by.username",
        read_only=True
    )

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = TicketAttachment
        fields = [
            "id",
            "ticket",
            "file",
            "file_url",
            "file_name",
            "uploaded_by",
            "uploaded_by_name",
            "created_at"
        ]

        read_only_fields = [
            "id",
            "uploaded_by",
            "created_at"
        ]

    def get_file_url(self, obj):
        """
        Return absolute file URL for frontend usage
        """
        request = self.context.get("request")
        if obj.file and hasattr(obj.file, "url"):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None