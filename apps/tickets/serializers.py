from rest_framework import serializers
from .models import Ticket
from apps.locations.models import Street


class TicketSerializer(serializers.ModelSerializer):

    # =========================
    # READABLE FIELDS
    # =========================
    team_name = serializers.CharField(source="team.name", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    # =========================
    # INPUT: street_id → street FK
    # =========================
    street_id = serializers.PrimaryKeyRelatedField(
        queryset=Street.objects.all(),
        source="street",
        write_only=True,
        required=False,
        allow_null=True
    )

    # =========================
    # OUTPUT: readable street
    # =========================
    street_name = serializers.CharField(source="street.name", read_only=True)

    # =========================
    # FULL LOCATION STRING
    # =========================
    location_full = serializers.SerializerMethodField()

    # =========================
    # ASSIGNED USER NAME
    # =========================
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            full_name = f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip()
            return full_name or obj.assigned_to.username
        return None

    # =========================
    # LOCATION BUILDER
    # =========================
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

    # =========================
    # META
    # =========================
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

            "customer_name",
            "customer_phone",
            "customer_email",

            "team_id",
            "assigned_to_id",

            # INPUT
            "street_id",

            # OUTPUT
            "street_name",
            "team_name",
            "assigned_to_name",
            "location_full",
        ]