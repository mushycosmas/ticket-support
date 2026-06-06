from rest_framework import serializers
from .models import Ticket, TicketAttachment, Customer, TicketHistory
from apps.locations.models import Street, Ward, District, Region


# =========================
# LOCATION SERIALIZERS
# =========================
class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'code']


class DistrictSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    
    class Meta:
        model = District
        fields = ['id', 'name', 'code', 'region']


class WardSerializer(serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)
    
    class Meta:
        model = Ward
        fields = ['id', 'name', 'code', 'district']


class StreetSerializer(serializers.ModelSerializer):
    ward = WardSerializer(read_only=True)
    
    class Meta:
        model = Street
        fields = ['id', 'name', 'code', 'ward']


# =========================
# ATTACHMENTS
# =========================
class TicketAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = ["id", "file", "file_name", "created_at"]


# =========================
# CUSTOMER
# =========================
class CustomerSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="full_name", read_only=True)
    customer_email = serializers.EmailField(source="email", read_only=True)
    customer_phone = serializers.CharField(source="phone", read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "customer_name",
            "customer_email",
            "customer_phone",
            "company_name",
            "address",
            "city",
            "country",
            "total_tickets",
            "total_resolved",
            "total_open",
            "created_at",
        ]
        read_only_fields = ["total_tickets", "total_resolved", "total_open"]


# =========================
# TICKET HISTORY
# =========================
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


# =========================
# MAIN TICKET SERIALIZER
# =========================
class TicketSerializer(serializers.ModelSerializer):
    # -------- Customer read --------
    customer_detail = CustomerSerializer(source="customer", read_only=True)

    # -------- Customer write --------
    customer_email = serializers.EmailField(write_only=True, required=True)
    customer_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    customer_phone = serializers.CharField(write_only=True, required=False, allow_blank=True)

    # -------- Location (Full details) --------
    street_id = serializers.PrimaryKeyRelatedField(
        queryset=Street.objects.all(),
        source="street",
        write_only=True,
        required=False,
        allow_null=True
    )
    
    # Full location details (read-only)
    street_name = serializers.CharField(source="street.name", read_only=True)
    ward_name = serializers.CharField(source="street.ward.name", read_only=True)
    district_name = serializers.CharField(source="street.ward.district.name", read_only=True)
    region_name = serializers.CharField(source="street.ward.district.region.name", read_only=True)
    
    # Full location object (read-only)
    location_full = serializers.SerializerMethodField()
    location_details = serializers.SerializerMethodField()

    # -------- Assignment --------
    team_name = serializers.CharField(source="team.name", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    # -------- Attachments --------
    attachments = TicketAttachmentSerializer(many=True, read_only=True)

    # -------- HISTORY --------
    history = TicketHistorySerializer(many=True, read_only=True)

    # =========================
    # CREATE
    # =========================
    def create(self, validated_data):
        request = self.context.get("request")
        files = request.FILES.getlist("file") if request else []

        email = validated_data.pop("customer_email")
        name = validated_data.pop("customer_name", None)
        phone = validated_data.pop("customer_phone", None)

        # IMPORTANT: reuse customer (NO duplicates)
        customer, _ = Customer.get_or_create_customer(
            email=email,
            phone=phone,
            full_name=name
        )

        validated_data["customer"] = customer
        ticket = Ticket.objects.create(**validated_data)

        # attachments
        for f in files:
            TicketAttachment.objects.create(
                ticket=ticket,
                file=f,
                file_name=f.name,
                uploaded_by=request.user if request and request.user.is_authenticated else None
            )

        # initial history
        TicketHistory.objects.create(
            ticket=ticket,
            action='CREATED',
            comment="Ticket created",
            created_by=request.user if request and request.user.is_authenticated else None
        )

        return ticket

    # =========================
    # UPDATE + HISTORY LOGGING
    # =========================
    def update(self, instance, validated_data):
        request = self.context.get("request")
        old_status = instance.status

        # customer update
        email = validated_data.pop("customer_email", None)
        if email:
            customer, _ = Customer.get_or_create_customer(
                email=email,
                phone=validated_data.pop("customer_phone", None),
                full_name=validated_data.pop("customer_name", None)
            )
            instance.customer = customer

        # update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # AUTO HISTORY ON STATUS CHANGE
        if old_status != instance.status:
            TicketHistory.objects.create(
                ticket=instance,
                action='STATUS_CHANGED',
                comment=f"Status changed from {old_status} to {instance.status}",
                old_status=old_status,
                new_status=instance.status,
                created_by=request.user if request and request.user.is_authenticated else None
            )

        return instance

    # =========================
    # HELPERS
    # =========================
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return None
    
    def get_location_full(self, obj):
        """Return full location as a formatted string"""
        if not obj.street:
            return None
        
        parts = []
        if obj.street.name:
            parts.append(obj.street.name)
        if obj.street.ward and obj.street.ward.name:
            parts.append(obj.street.ward.name)
        if obj.street.ward and obj.street.ward.district and obj.street.ward.district.name:
            parts.append(obj.street.ward.district.name)
        if obj.street.ward and obj.street.ward.district and obj.street.ward.district.region and obj.street.ward.district.region.name:
            parts.append(obj.street.ward.district.region.name)
        
        return ", ".join(parts) if parts else None
    
    def get_location_details(self, obj):
        """Return full location as a nested object"""
        if not obj.street:
            return None
        
        location = {
            'street': obj.street.name if obj.street else None,
            'street_id': obj.street.id if obj.street else None,
        }
        
        if obj.street and obj.street.ward:
            location['ward'] = obj.street.ward.name
            location['ward_id'] = obj.street.ward.id
            
            if obj.street.ward.district:
                location['district'] = obj.street.ward.district.name
                location['district_id'] = obj.street.ward.district.id
                
                if obj.street.ward.district.region:
                    location['region'] = obj.street.ward.district.region.name
                    location['region_id'] = obj.street.ward.district.region.id
        
        return location

    # =========================
    # META
    # =========================
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

            # assignment
            "team",
            "team_name",
            "assigned_to",
            "assigned_to_name",
            "assigned_by",

            # location (full details)
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
        ]
        extra_kwargs = {
            'customer': {'required': False, 'allow_null': True},
        }