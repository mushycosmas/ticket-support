from rest_framework import serializers
from .models import Ticket, TicketAttachment
from apps.locations.models import Street


class TicketAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = ["id", "file", "file_name", "created_at"]


class TicketSerializer(serializers.ModelSerializer):

    # =====================
    # READ FIELDS
    # =====================
    team_name = serializers.CharField(source="team.name", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    street_id = serializers.PrimaryKeyRelatedField(
        queryset=Street.objects.all(),
        source="street",
        write_only=True,
        required=False,
        allow_null=True
    )

    street_name = serializers.CharField(source="street.name", read_only=True)
    location_full = serializers.SerializerMethodField()

    attachments = TicketAttachmentSerializer(many=True, read_only=True)

    # =====================
    # CREATE FILE SUPPORT
    # =====================
    def create(self, validated_data):
        request = self.context.get("request")
        files = request.FILES.getlist("file") if request else []

        ticket = Ticket.objects.create(**validated_data)

        # SAVE FILES HERE
        for f in files:
            TicketAttachment.objects.create(
                ticket=ticket,
                file=f,
                file_name=f.name,
                uploaded_by=request.user if request and request.user.is_authenticated else None
            )

        return ticket

    # =====================
    # HELPERS
    # =====================
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return (
                f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip()
                or obj.assigned_to.username
            )
        return None

    def get_location_full(self, obj):
        street = obj.street
        ward = street.ward if street else None
        district = ward.district if ward else None
        region = district.region if district else None

        parts = []
        if region:
            parts.append(region.name)
        if district:
            parts.append(district.name)
        if ward:
            parts.append(ward.name)
        if street:
            parts.append(street.name)

        return ", ".join(parts) if parts else None

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
            "ticket_number",
            "customer_name",
            "customer_phone",
            "customer_email",

            "team_id",
            "assigned_to_id",

            "street_id",

            "street_name",
            "team_name",
            "assigned_to_name",
            "location_full",

            "attachments",  # ✅ IMPORTANT
        ]