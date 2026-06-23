from rest_framework import serializers
from apps.tickets.models import Ticket, TicketAttachment, Customer, TicketHistory, IssueTemplate
from apps.locations.models import Street
from .customer_serializer import CustomerSerializer
from .attachment_serializer import TicketAttachmentSerializer
from .history_serializer import TicketHistorySerializer
from .issue_template_serializer import IssueTemplateSerializer


class TicketSerializer(serializers.ModelSerializer):

    # =====================
    # CUSTOMER (read & write)
    # =====================
    customer_detail = CustomerSerializer(source="customer", read_only=True)

    customer_email = serializers.EmailField(write_only=True, required=True)
    customer_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    customer_phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    customer_nida = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    customer_gender = serializers.ChoiceField(
        choices=['M', 'F', 'O', 'N'],
        write_only=True,
        required=False,
        allow_null=True
    )

    # =====================
    # TEMPLATE
    # =====================
    template_id = serializers.PrimaryKeyRelatedField(
        queryset=IssueTemplate.objects.all(),
        source="template",
        write_only=True,
        required=False,
        allow_null=True
    )
    template_name = serializers.CharField(source="template.name", read_only=True)
    template_detail = IssueTemplateSerializer(source="template", read_only=True)

    # =====================
    # LOCATION
    # =====================
    street_id = serializers.PrimaryKeyRelatedField(
        queryset=Street.objects.all(),
        source="street",
        write_only=True,
        required=False,
        allow_null=True
    )
    street_name = serializers.CharField(source="street.name", read_only=True)
    ward_name = serializers.CharField(source="street.ward.name", read_only=True)
    district_name = serializers.CharField(source="street.ward.district.name", read_only=True)
    region_name = serializers.CharField(source="street.ward.district.region.name", read_only=True)
    location_full = serializers.SerializerMethodField()
    location_details = serializers.SerializerMethodField()

    # =====================
    # ASSIGNMENT
    # =====================
    team_name = serializers.CharField(source="team.name", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    # =====================
    # RELATIONS
    # =====================
    attachments = TicketAttachmentSerializer(many=True, read_only=True)
    history = TicketHistorySerializer(many=True, read_only=True)

    # =====================
    # CREATE
    # =====================
    def create(self, validated_data):
        request = self.context.get("request")
        files = request.FILES.getlist("file") if request else []

        # Extract customer data
        email = validated_data.pop("customer_email")
        name = validated_data.pop("customer_name", None)
        phone = validated_data.pop("customer_phone", None)
        nida = validated_data.pop("customer_nida", None)
        gender = validated_data.pop("customer_gender", None)

        template = validated_data.get("template", None)

        # Auto fill from template
        if template:
            validated_data.setdefault("title", template.name)
            validated_data.setdefault("description", template.description)
            validated_data.setdefault("priority", template.suggested_priority)
            validated_data.setdefault("category", template.category)

        # Create or get customer with extra fields
        customer, _ = Customer.get_or_create_customer(
            email=email,
            phone=phone,
            full_name=name,
            nida_number=nida,
            gender=gender
        )

        validated_data["customer"] = customer
        ticket = Ticket.objects.create(**validated_data)

        # Attachments
        for f in files:
            TicketAttachment.objects.create(
                ticket=ticket,
                file=f,
                file_name=f.name,
                uploaded_by=request.user if request and request.user.is_authenticated else None
            )

        # History
        TicketHistory.objects.create(
            ticket=ticket,
            action="CREATED",
            comment="Ticket created",
            created_by=request.user if request and request.user.is_authenticated else None
        )

        return ticket

    # =====================
    # UPDATE
    # =====================
    def update(self, instance, validated_data):
        request = self.context.get("request")
        old_status = instance.status

        # Update customer if email is provided
        email = validated_data.pop("customer_email", None)
        if email:
            name = validated_data.pop("customer_name", None)
            phone = validated_data.pop("customer_phone", None)
            nida = validated_data.pop("customer_nida", None)
            gender = validated_data.pop("customer_gender", None)

            customer, _ = Customer.get_or_create_customer(
                email=email,
                phone=phone,
                full_name=name,
                nida_number=nida,
                gender=gender
            )
            instance.customer = customer

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if old_status != instance.status:
            TicketHistory.objects.create(
                ticket=instance,
                action="STATUS_CHANGED",
                comment=f"Status changed from {old_status} to {instance.status}",
                old_status=old_status,
                new_status=instance.status,
                created_by=request.user if request and request.user.is_authenticated else None
            )

        return instance

    # =====================
    # HELPERS
    # =====================
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return None

    def get_location_full(self, obj):
        if not obj.street:
            return None
        parts = [
            obj.street.name,
            obj.street.ward.name if obj.street.ward else None,
            obj.street.ward.district.name if obj.street.ward and obj.street.ward.district else None,
            obj.street.ward.district.region.name if obj.street.ward and obj.street.ward.district and obj.street.ward.district.region else None,
        ]
        return ", ".join(p for p in parts if p)

    def get_location_details(self, obj):
        if not obj.street:
            return None
        return {
            "street": obj.street.name,
            "ward": obj.street.ward.name if obj.street.ward else None,
            "district": obj.street.ward.district.name if obj.street.ward and obj.street.ward.district else None,
            "region": obj.street.ward.district.region.name if obj.street.ward and obj.street.ward.district and obj.street.ward.district.region else None,
        }

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_number",
            "title",
            "description",
            "status",
            "priority",
            "created_at",
            "updated_at",
            "channel",
            "resolved_at",

            # customer
            "customer",
            "customer_detail",
            "customer_email",
            "customer_name",
            "customer_phone",
            "customer_nida",
            "customer_gender",

            # template
            "template",
            "template_id",
            "template_name",
            "template_detail",

            # assignment
            "team",
            "team_name",
            "assigned_to",
            "assigned_to_name",
            "assigned_by",

            # location
            "street",
            "street_id",
            "street_name",
            "ward_name",
            "district_name",
            "region_name",
            "location_full",
            "location_details",

            # relations
            "attachments",
            "history",
            "deleted_at"
        ]
        extra_kwargs = {
            "customer": {"required": False, "allow_null": True},
        }