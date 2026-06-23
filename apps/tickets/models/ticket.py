# apps/tickets/models/ticket.py
from django.db import models
from django.utils import timezone

from .base import TimeStampedModel

USER_MODEL = "users.User"
TEAM_MODEL = "users.Team"
STREET_MODEL = "locations.Street"
CUSTOMER_MODEL = "Customer"


# ======================
# SOFT DELETE MANAGER
# ======================
class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted records by default."""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class Ticket(TimeStampedModel):
    """
    Ticket model (ITSM-ready structure) with soft delete support.

    Supports:
    - Customer tickets
    - Teams & assignment
    - Street location
    - Issue templates
    - Categories
    - Channel-based routing
    - Soft delete (hide instead of delete)
    """

    # ======================
    # IDENTIFIER
    # ======================
    ticket_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        db_index=True
    )

    # ======================
    # RELATIONSHIPS
    # ======================
    customer = models.ForeignKey(
        CUSTOMER_MODEL,
        on_delete=models.PROTECT,
        related_name="tickets"
    )

    team = models.ForeignKey(
        TEAM_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets"
    )

    assigned_to = models.ForeignKey(
        USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets"
    )

    assigned_by = models.ForeignKey(
        USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_assigned_by_me"
    )

    street = models.ForeignKey(
        STREET_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets"
    )

    # ======================
    # ISSUE TEMPLATE
    # ======================
    template = models.ForeignKey(
        "tickets.IssueTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets"
    )

    # ======================
    # CATEGORY
    # ======================
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets"
    )

    # ======================
    # CHANNEL
    # ======================
    channel = models.ForeignKey(
        "channels.Channel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets"
    )

    # ======================
    # TICKET DETAILS
    # ======================
    title = models.CharField(max_length=255)
    description = models.TextField()

    priority = models.CharField(
        max_length=20,
        default="MEDIUM"
    )

    status = models.CharField(
        max_length=20,
        default="OPEN"
    )

    # ======================
    # TIMESTAMPS
    # ======================
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ======================
    # SOFT DELETE FIELD
    # ======================
    deleted_at = models.DateTimeField(null=True, blank=True)

    # ======================
    # MANAGERS
    # ======================
    objects = SoftDeleteManager()          # Excludes soft-deleted by default
    all_objects = models.Manager()         # Includes all records (for admin/reports)

    # ======================
    # SOFT DELETE METHODS
    # ======================
    def soft_delete(self):
        """Mark as deleted without removing from database."""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        """Restore a soft-deleted ticket."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    # ======================
    # SAVE OVERRIDE
    # ======================
    def save(self, *args, **kwargs):
        """
        Auto-generate ticket number
        Update customer statistics
        """
        if not self.ticket_number:
            self.ticket_number = self._generate_ticket_number()

        super().save(*args, **kwargs)

        if self.customer:
            self.customer.update_statistics()

    # ======================
    # TICKET NUMBER GENERATOR
    # ======================
    def _generate_ticket_number(self):
        today = timezone.now().strftime("%Y%m%d")

        last_ticket = Ticket.objects.filter(
            ticket_number__startswith=f"TKT-{today}"
        ).order_by("-id").first()

        if last_ticket and last_ticket.ticket_number:
            try:
                last_number = int(last_ticket.ticket_number.split("-")[-1])
            except (ValueError, IndexError):
                last_number = 0
        else:
            last_number = 0

        return f"TKT-{today}-{last_number + 1:06d}"

    # ======================
    # HELPERS
    # ======================
    @property
    def customer_name(self):
        return self.customer.full_name if self.customer else None

    @property
    def customer_email(self):
        return self.customer.email if self.customer else None

    @property
    def customer_phone(self):
        return self.customer.phone if self.customer else None

    # ======================
    # STRING REPRESENTATION
    # ======================
    def __str__(self):
        return f"{self.ticket_number or self.id} - {self.title}"
    