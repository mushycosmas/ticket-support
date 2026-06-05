from django.db import models
from django.utils import timezone
from .choices import TicketChannel, TicketStatus, TicketPriority
from .base import TimeStampedModel

USER_MODEL = "users.User"
TEAM_MODEL = "users.Team"
STREET_MODEL = "locations.Street"

class Ticket(TimeStampedModel):
    # Identifier
    ticket_number = models.CharField(
        max_length=50, unique=True, blank=True, null=True, db_index=True
    )
    
    # Customer Relationship (ONLY THIS - no customer_name, email, phone)
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.PROTECT,
        related_name="tickets"
    )
    
    # Ticket Info
    channel = models.CharField(max_length=20, choices=TicketChannel.CHOICES, default='WEB')
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=TicketPriority.CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=TicketStatus.CHOICES, default='OPEN')
    
    # Workflow
    team = models.ForeignKey(TEAM_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets")
    assigned_to = models.ForeignKey(USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets")
    assigned_by = models.ForeignKey(USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets_assigned_by_me")
    
    # Location
    street = models.ForeignKey(STREET_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets")
    
    # Additional timestamps
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self._generate_ticket_number()
        super().save(*args, **kwargs)
        
        # Update customer statistics
        if self.customer:
            self.customer.update_statistics()
    
    def _generate_ticket_number(self):
        today = timezone.now().strftime("%Y%m%d")
        last_ticket = Ticket.objects.filter(
            ticket_number__startswith=f"TKT-{today}"
        ).order_by("id").last()
        
        if last_ticket and last_ticket.ticket_number:
            try:
                last_number = int(last_ticket.ticket_number.split("-")[-1])
            except ValueError:
                last_number = 0
        else:
            last_number = 0
        
        return f"TKT-{today}-{last_number + 1:06d}"
    
    @property
    def customer_name(self):
        """Helper to get customer name from related customer"""
        return self.customer.full_name if self.customer else None
    
    @property
    def customer_email(self):
        """Helper to get customer email from related customer"""
        return self.customer.email if self.customer else None
    
    @property
    def customer_phone(self):
        """Helper to get customer phone from related customer"""
        return self.customer.phone if self.customer else None
    
    def __str__(self):
        return f"{self.ticket_number or self.id} - {self.title}"