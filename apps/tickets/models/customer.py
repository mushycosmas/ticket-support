from django.db import models
from django.db.models import Q
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth import get_user_model

User = get_user_model()


# ======================
# GENDER ENUM
# ======================
class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"


# ======================
# CUSTOMER MODEL
# ======================
class Customer(models.Model):
    """Customer model to store customer information separately from tickets"""

    # ======================
    # BASIC INFORMATION
    # ======================
    full_name = models.CharField(max_length=255, db_index=True)

    # ✅ Make email nullable and allow blank
    email = models.EmailField(
        validators=[EmailValidator(message="Enter a valid email address")],
        db_index=True,
        null=True,          # ✅ Allow NULL in database
        blank=True          # ✅ Allow blank in forms
    )

    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be in international format"
            )
        ],
        db_index=True
    )

    # ======================
    # IDENTITY FIELDS
    # ======================
    nida_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text="National ID number (NIDA)"
    )

    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        null=True,
        blank=True
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
    country = models.CharField(max_length=100, default="Tanzania")
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    # ======================
    # PREFERENCES
    # ======================
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ("EMAIL", "Email"),
            ("PHONE", "Phone"),
            ("SMS", "SMS"),
            ("WHATSAPP", "WhatsApp"),
        ],
        default="EMAIL"
    )

    preferred_language = models.CharField(max_length=10, default="en")

    # ======================
    # META DATA
    # ======================
    notes = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customers_created"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    last_ticket_created = models.DateTimeField(null=True, blank=True)

    # ======================
    # STATISTICS
    # ======================
    total_tickets = models.PositiveIntegerField(default=0)
    total_resolved = models.PositiveIntegerField(default=0)
    total_open = models.PositiveIntegerField(default=0)

    # ======================
    # META
    # ======================
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["full_name"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(gender__in=Gender.values) | Q(gender__isnull=True),
                name="valid_gender_constraint",
            )
        ]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        if self.full_name:
            return f"{self.full_name} ({self.email or 'No Email'})"
        return f"{self.email or self.phone or 'Customer'}"

    # ======================
    # UPDATE STATISTICS
    # ======================
    def update_statistics(self):
        from .ticket import Ticket

        self.total_tickets = self.tickets.count()
        self.total_resolved = self.tickets.filter(status="RESOLVED").count()
        self.total_open = self.tickets.filter(
            status__in=["OPEN", "ASSIGNED", "IN_PROGRESS"]
        ).count()

        last_ticket = self.tickets.order_by("-created_at").first()
        if last_ticket:
            self.last_ticket_created = last_ticket.created_at

        self.save(update_fields=[
            "total_tickets",
            "total_resolved",
            "total_open",
            "last_ticket_created",
        ])

    # ======================
    # SMART GET OR CREATE (UPDATED)
    # ======================
    @classmethod
    def get_or_create_customer(cls, email=None, phone=None, full_name=None, **kwargs):
        """
        Get or create a customer.
        
        Priority:
        1. Find by NIDA number
        2. Find by Email (if provided)
        3. Find by Phone (if provided)
        
        Args:
            email: Customer's email (optional)
            phone: Customer's phone (required)
            full_name: Customer's full name (optional)
            **kwargs: Additional fields (nida_number, gender, etc.)
        
        Returns:
            tuple: (customer, created)
        """
        nida = kwargs.get("nida_number")
        gender = kwargs.get("gender")
        
        # Build query
        query = Q()
        
        # If email is provided, add to query
        if email and email.strip():
            query |= Q(email=email.strip())
        
        # If phone is provided, add to query
        if phone and phone.strip():
            query |= Q(phone=phone.strip())
        
        # If NIDA is provided, add to query
        if nida and nida.strip():
            query |= Q(nida_number=nida.strip())
        
        # If no criteria provided, create new customer
        if not query:
            customer = cls.objects.create(
                full_name=full_name or "Unknown",
                email=email.strip() if email else None,
                phone=phone.strip() if phone else None,
                nida_number=nida.strip() if nida else None,
                gender=gender,
                **{k: v for k, v in kwargs.items() if k not in ("nida_number", "gender")}
            )
            return customer, True
        
        # Try to find existing customer
        customer = cls.objects.filter(query).first()
        
        if customer:
            # Update existing customer with latest info
            if full_name:
                customer.full_name = full_name
            
            if email and email.strip():
                customer.email = email.strip()
            
            if phone and phone.strip():
                customer.phone = phone.strip()
            
            if nida and nida.strip():
                customer.nida_number = nida.strip()
            
            if gender:
                customer.gender = gender
            
            customer.save()
            return customer, False
        
        # Create new customer
        customer = cls.objects.create(
            full_name=full_name or email or phone or "Unknown",
            email=email.strip() if email else None,
            phone=phone.strip() if phone else None,
            nida_number=nida.strip() if nida else None,
            gender=gender,
            **{k: v for k, v in kwargs.items() if k not in ("nida_number", "gender")}
        )
        return customer, True