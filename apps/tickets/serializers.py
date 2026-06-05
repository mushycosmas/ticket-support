from rest_framework import serializers
from .models import Ticket, TicketAttachment, Customer
from apps.locations.models import Street


class TicketAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = ["id", "file", "file_name", "created_at"]


class CustomerSerializer(serializers.ModelSerializer):
    # Rename fields for response
    customer_name = serializers.CharField(source='full_name', read_only=True)
    customer_email = serializers.EmailField(source='email', read_only=True)
    customer_phone = serializers.CharField(source='phone', read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            "id", 
            "customer_name",      # renamed from full_name
            "customer_email",     # renamed from email
            "customer_phone",     # renamed from phone
            "alternate_phone",
            "company_name", 
            "address", 
            "city", 
            "country",
            "total_tickets", 
            "total_resolved", 
            "total_open",
            "created_at", 
            "last_ticket_created"
        ]
        read_only_fields = ["total_tickets", "total_resolved", "total_open", "created_at"]


class TicketSerializer(serializers.ModelSerializer):
    # Customer nested serializer for read (now returns customer_name, customer_email, customer_phone)
    customer_detail = CustomerSerializer(source="customer", read_only=True)
    
    # Write-only field for creating ticket with customer
    customer_email = serializers.EmailField(write_only=True, required=True)
    customer_name = serializers.CharField(write_only=True, required=False, allow_null=True)
    customer_phone = serializers.CharField(write_only=True, required=False, allow_null=True)
    
    # Other fields
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

    def __init__(self, *args, **kwargs):
        """Make customer field optional in serializer"""
        super().__init__(*args, **kwargs)
        # Make customer field not required
        if 'customer' in self.fields:
            self.fields['customer'].required = False
            self.fields['customer'].allow_null = True

    def create(self, validated_data):
        request = self.context.get("request")
        files = request.FILES.getlist("file") if request else []
        
        # Extract customer data
        customer_email = validated_data.pop('customer_email', None)
        customer_name = validated_data.pop('customer_name', None)
        customer_phone = validated_data.pop('customer_phone', None)
        
        if not customer_email:
            raise serializers.ValidationError({"customer_email": "Customer email is required"})
        
        # Create or get customer
        customer, created = Customer.get_or_create_customer(
            email=customer_email,
            full_name=customer_name,
            phone=customer_phone
        )
        
        if not customer:
            raise serializers.ValidationError({"customer_email": "Could not create/get customer"})
        
        validated_data['customer'] = customer
        
        # Create ticket
        ticket = Ticket.objects.create(**validated_data)
        
        # Save attachments
        for f in files:
            TicketAttachment.objects.create(
                ticket=ticket,
                file=f,
                file_name=f.name,
                uploaded_by=request.user if request and request.user.is_authenticated else None
            )
        
        return ticket

    def update(self, instance, validated_data):
        # Handle customer update if email provided
        customer_email = validated_data.pop('customer_email', None)
        if customer_email:
            customer, created = Customer.get_or_create_customer(
                email=customer_email,
                full_name=validated_data.pop('customer_name', None),
                phone=validated_data.pop('customer_phone', None)
            )
            if customer:
                instance.customer = customer
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

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
            "ticket_number",
            "title",
            "description",
            "status",
            "priority",
            "created_at",
            "updated_at",
            "channel",
            "resolved_at",
            
            # Customer relations
            "customer",
            "customer_detail",
            "customer_email",  # write-only
            "customer_name",   # write-only
            "customer_phone",  # write-only
            
            # Assignment
            "team",
            "team_name",
            "assigned_to",
            "assigned_to_name",
            "assigned_by",
            
            # Location
            "street",
            "street_id",
            "street_name",
            "location_full",
            
            # Attachments
            "attachments",
        ]
        extra_kwargs = {
            'customer': {'required': False, 'allow_null': True},
        }