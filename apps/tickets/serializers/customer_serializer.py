from rest_framework import serializers
from ..models.customer import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model"""
    
    class Meta:
        model = Customer
        fields = [
            'id', 'full_name', 'email', 'phone', 'alternate_phone',
            'company_name', 'address', 'city', 'state', 'country', 'postal_code',
            'preferred_contact_method', 'preferred_language', 'notes',
            'total_tickets', 'total_resolved', 'total_open',
            'last_ticket_created', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_tickets', 'total_resolved', 'total_open', 
                           'last_ticket_created', 'created_at', 'updated_at']


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Detailed Customer serializer with tickets"""
    tickets = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'full_name', 'email', 'phone', 'alternate_phone',
            'company_name', 'address', 'city', 'state', 'country', 'postal_code',
            'preferred_contact_method', 'preferred_language', 'notes',
            'total_tickets', 'total_resolved', 'total_open',
            'last_ticket_created', 'created_at', 'updated_at', 'tickets'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_tickets(self, obj):
        from ..models.ticket import Ticket
        from .ticket_serializer import TicketSerializer
        
        tickets = Ticket.objects.filter(customer=obj).order_by('-created_at')
        return TicketSerializer(tickets, many=True).data


class CustomerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new customer"""
    
    class Meta:
        model = Customer
        fields = [
            'full_name', 'email', 'phone', 'alternate_phone',
            'company_name', 'address', 'city', 'state', 'country', 'postal_code',
            'preferred_contact_method', 'preferred_language', 'notes'
        ]
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if Customer.objects.filter(email=value).exists():
            raise serializers.ValidationError("Customer with this email already exists")
        return value
    
    def validate_phone(self, value):
        """Validate phone uniqueness"""
        if Customer.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Customer with this phone already exists")
        return value


class CustomerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating customer"""
    
    class Meta:
        model = Customer
        fields = [
            'full_name', 'email', 'phone', 'alternate_phone',
            'company_name', 'address', 'city', 'state', 'country', 'postal_code',
            'preferred_contact_method', 'preferred_language', 'notes'
        ]