from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class Customer(models.Model):
    """Customer model to store customer information separately from tickets"""
    
    # Basic Information
    full_name = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(message="Enter a valid email address")],
        db_index=True
    )
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be in international format"
        )],
        db_index=True
    )
    
    # Optional fields
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Address Information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='Tanzania')
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Preferences
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('EMAIL', 'Email'),
            ('PHONE', 'Phone'),
            ('SMS', 'SMS'),
            ('WHATSAPP', 'WhatsApp')
        ],
        default='EMAIL'
    )
    preferred_language = models.CharField(max_length=10, default='en')
    
    # Metadata
    notes = models.TextField(blank=True, null=True, help_text="Internal notes about the customer")
    
    # Relations
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers_created'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_ticket_created = models.DateTimeField(null=True, blank=True)
    
    # Statistics (denormalized for performance)
    total_tickets = models.IntegerField(default=0)
    total_resolved = models.IntegerField(default=0)
    total_open = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'phone']),
            models.Index(fields=['full_name']),
            models.Index(fields=['-total_tickets']),
        ]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def update_statistics(self):
        """Update customer ticket statistics"""
        from .ticket import Ticket  # Import here to avoid circular imports
        
        self.total_tickets = self.tickets.count()
        self.total_resolved = self.tickets.filter(status='RESOLVED').count()
        self.total_open = self.tickets.filter(status__in=['OPEN', 'ASSIGNED', 'IN_PROGRESS']).count()
        
        last_ticket = self.tickets.order_by('-created_at').first()
        if last_ticket:
            self.last_ticket_created = last_ticket.created_at
        
        self.save(update_fields=['total_tickets', 'total_resolved', 'total_open', 'last_ticket_created'])
    
    @classmethod
    def get_or_create_customer(cls, email, full_name=None, phone=None, **kwargs):
        """Get existing customer or create new one"""
        customer, created = cls.objects.get_or_create(
            email=email.lower(),
            defaults={
                'full_name': full_name or email.split('@')[0],
                'phone': phone or 'Not Provided',
                **kwargs
            }
        )
        return customer, created