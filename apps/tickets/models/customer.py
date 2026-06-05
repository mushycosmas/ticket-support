from django.db import models
from django.db.models import Q
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Customer(models.Model):
    """Customer model to store customer information separately from tickets"""

    # ======================
    # BASIC INFORMATION
    # ======================
    full_name = models.CharField(max_length=255, db_index=True)

    email = models.EmailField(
        validators=[EmailValidator(message="Enter a valid email address")],
        db_index=True
    )

    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in international format"
            )
        ],
        db_index=True
    )

    # ======================
    # OPTIONAL FIELDS
    # ======================
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)

    # ======================
    # ADDRESS INFO
    # ======================
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='Tanzania')
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    # ======================
    # PREFERENCES
    # ======================
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

    # ======================
    # META DATA
    # ======================
    notes = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers_created'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    last_ticket_created = models.DateTimeField(null=True, blank=True)

    # ======================
    # STATISTICS
    # ======================
    total_tickets = models.IntegerField(default=0)
    total_resolved = models.IntegerField(default=0)
    total_open = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['full_name']),
        ]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    # ======================
    # UPDATE STATISTICS
    # ======================
    def update_statistics(self):
        from .ticket import Ticket

        self.total_tickets = self.tickets.count()
        self.total_resolved = self.tickets.filter(status='RESOLVED').count()
        self.total_open = self.tickets.filter(
            status__in=['OPEN', 'ASSIGNED', 'IN_PROGRESS']
        ).count()

        last_ticket = self.tickets.order_by('-created_at').first()
        if last_ticket:
            self.last_ticket_created = last_ticket.created_at

        self.save(update_fields=[
            'total_tickets',
            'total_resolved',
            'total_open',
            'last_ticket_created'
        ])

    # ======================
    # SMART GET OR CREATE
    # ======================
    @classmethod
    def get_or_create_customer(cls, email, phone, full_name=None, **kwargs):
        """
        RULE:
        - If email OR phone exists → reuse customer
        - Otherwise create new customer
        """

        customer = cls.objects.filter(
            Q(email=email) | Q(phone=phone)
        ).first()

        if customer:
            # update latest info
            customer.full_name = full_name or customer.full_name
            customer.email = email
            customer.phone = phone

            for key, value in kwargs.items():
                setattr(customer, key, value)

            customer.save()
            return customer, False

        customer = cls.objects.create(
            full_name=full_name or "Unknown",
            email=email,
            phone=phone,
            **kwargs
        )

        return customer, True