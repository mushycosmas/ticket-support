from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
# =====================
# CONSTANTS
# =====================
USER_MODEL = "users.User"
TEAM_MODEL = "users.Team"
STREET_MODEL = "locations.Street"


# =====================
# TICKET MODEL
# =====================
class Ticket(models.Model):

    CHANNEL_CHOICES = [
        ('PHONE', 'Phone'),
        ('WALKIN', 'Walk-in'),
        ('EMAIL', 'Email'),
        ('CHAT', 'Chat'),
        ('WEB', 'Web Form'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    # =====================
    # IDENTIFIER
    # =====================
    ticket_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        db_index=True
    )

    # =====================
    # CUSTOMER INFO
    # =====================
    customer_name = models.CharField(max_length=255, default='Unknown')
    customer_phone = models.CharField(max_length=100, default='Not Provided')
    customer_email = models.CharField(max_length=100, default='Not Provided')

    # =====================
    # TICKET INFO
    # =====================
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='WEB')
    title = models.CharField(max_length=255)
    description = models.TextField()

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    # =====================
    # WORKFLOW
    # =====================
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

    # =====================
    # LOCATION
    # =====================
    street = models.ForeignKey(
        STREET_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets"
    )

    # =====================
    # TIMESTAMPS
    # =====================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # =====================
    # SAVE OVERRIDE (TICKET NUMBER GENERATOR)
    # =====================
    def save(self, *args, **kwargs):

        if not self.ticket_number:
            today = timezone.now().strftime("%Y%m%d")

            last_ticket = Ticket.objects.filter(
                ticket_number__startswith=f"TKT-{today}"
            ).order_by("id").last()

            if last_ticket and last_ticket.ticket_number:
                try:
                    last_number = int(last_ticket.ticket_number.split("-")[-1])
                except:
                    last_number = 0
            else:
                last_number = 0

            self.ticket_number = f"TKT-{today}-{last_number + 1:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number or self.id} - {self.title}"


# =====================
# TICKET ATTACHMENT
# =====================
class TicketAttachment(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="attachments"
    )

    uploaded_by = models.ForeignKey(
        USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    file = models.FileField(upload_to="ticket_attachments/")
    file_name = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file and not self.file_name:
            self.file_name = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.file_name or "Attachment"


User = get_user_model()

class TicketHistory(models.Model):
    class ActionType(models.TextChoices):
        CREATED = 'CREATED', 'Ticket Created'
        UPDATED = 'UPDATED', 'Ticket Updated'
        COMMENTED = 'COMMENTED', 'Comment Added'
        STATUS_CHANGED = 'STATUS_CHANGED', 'Status Changed'
        PRIORITY_CHANGED = 'PRIORITY_CHANGED', 'Priority Changed'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        UNASSIGNED = 'UNASSIGNED', 'Unassigned'
        ATTACHMENT = 'ATTACHMENT', 'Attachment Added'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'
        REOPENED = 'REOPENED', 'Reopened'
    
    ticket = models.ForeignKey(
        "Ticket",
        on_delete=models.CASCADE,
        related_name="histories"
    )
    
    # Main fields
    action = models.CharField(
        max_length=50,
        choices=ActionType.choices,
        db_index=True,
        help_text="Type of action performed"
    )
    
    # Status tracking (for STATUS_CHANGED action)
    old_status = models.CharField(max_length=50, null=True, blank=True)
    new_status = models.CharField(max_length=50, null=True, blank=True)
    
    # Priority tracking (for PRIORITY_CHANGED action)
    old_priority = models.CharField(max_length=20, null=True, blank=True)
    new_priority = models.CharField(max_length=20, null=True, blank=True)
    
    # Assignment tracking (for ASSIGNED/UNASSIGNED actions)
    old_assignee = models.CharField(max_length=255, null=True, blank=True)
    new_assignee = models.CharField(max_length=255, null=True, blank=True)
    
    # Comment content (for COMMENTED action)
    comment = models.TextField(
        null=True, 
        blank=True,
        validators=[MinLengthValidator(1, "Comment cannot be empty")]
    )
    
    # Additional metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data like attachment names, old values, etc."
    )
    
    # User who performed the action
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_histories"
    )
    
    # IP Address tracking (optional)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Ticket History"
        verbose_name_plural = "Ticket Histories"
        indexes = [
            models.Index(fields=['ticket', '-created_at']),
            models.Index(fields=['action', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.ticket.ticket_number} - {self.get_action_display()} by {self.created_by or 'System'} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def display_message(self):
        """Generate a user-friendly message for the timeline"""
        if self.action == self.ActionType.CREATED:
            return f"Ticket created"
        elif self.action == self.ActionType.COMMENTED:
            return self.comment
        elif self.action == self.ActionType.STATUS_CHANGED:
            return f"Status changed from {self.old_status} to {self.new_status}"
        elif self.action == self.ActionType.PRIORITY_CHANGED:
            return f"Priority changed from {self.old_priority} to {self.new_priority}"
        elif self.action == self.ActionType.ASSIGNED:
            return f"Assigned to {self.new_assignee}"
        elif self.action == self.ActionType.UNASSIGNED:
            return f"Unassigned from {self.old_assignee}"
        elif self.action == self.ActionType.RESOLVED:
            return "Ticket resolved"
        elif self.action == self.ActionType.CLOSED:
            return "Ticket closed"
        elif self.action == self.ActionType.REOPENED:
            return "Ticket reopened"
        elif self.action == self.ActionType.ATTACHMENT:
            attachments = self.metadata.get('attachments', [])
            if attachments:
                return f"Added {len(attachments)} attachment(s): {', '.join(attachments)}"
            return "Attachment(s) added"
        else:
            return self.metadata.get('message', 'Ticket updated')
    
    @property
    def display_type(self):
        """Get the display type for frontend timeline"""
        type_map = {
            self.ActionType.CREATED: 'info',
            self.ActionType.COMMENTED: 'comment',
            self.ActionType.STATUS_CHANGED: 'update',
            self.ActionType.PRIORITY_CHANGED: 'update',
            self.ActionType.ASSIGNED: 'update',
            self.ActionType.UNASSIGNED: 'update',
            self.ActionType.RESOLVED: 'resolution',
            self.ActionType.CLOSED: 'resolution',
            self.ActionType.REOPENED: 'info',
            self.ActionType.ATTACHMENT: 'update',
            self.ActionType.UPDATED: 'update',
        }
        return type_map.get(self.action, 'info')
    
    @classmethod
    def log_creation(cls, ticket, user=None, ip_address=None):
        """Log ticket creation"""
        return cls.objects.create(
            ticket=ticket,
            action=cls.ActionType.CREATED,
            created_by=user,
            ip_address=ip_address,
            metadata={'message': f'Ticket "{ticket.title}" was created'}
        )
    
    @classmethod
    def log_comment(cls, ticket, comment, user=None, ip_address=None):
        """Log a comment on ticket"""
        return cls.objects.create(
            ticket=ticket,
            action=cls.ActionType.COMMENTED,
            comment=comment,
            created_by=user,
            ip_address=ip_address
        )
    
    @classmethod
    def log_status_change(cls, ticket, old_status, new_status, user=None, ip_address=None):
        """Log status change"""
        return cls.objects.create(
            ticket=ticket,
            action=cls.ActionType.STATUS_CHANGED,
            old_status=old_status,
            new_status=new_status,
            created_by=user,
            ip_address=ip_address,
            metadata={'old_status': old_status, 'new_status': new_status}
        )
    
    @classmethod
    def log_priority_change(cls, ticket, old_priority, new_priority, user=None, ip_address=None):
        """Log priority change"""
        return cls.objects.create(
            ticket=ticket,
            action=cls.ActionType.PRIORITY_CHANGED,
            old_priority=old_priority,
            new_priority=new_priority,
            created_by=user,
            ip_address=ip_address,
            metadata={'old_priority': old_priority, 'new_priority': new_priority}
        )
    
    @classmethod
    def log_assignment(cls, ticket, old_assignee, new_assignee, user=None, ip_address=None):
        """Log assignment change"""
        action = cls.ActionType.ASSIGNED if new_assignee else cls.ActionType.UNASSIGNED
        return cls.objects.create(
            ticket=ticket,
            action=action,
            old_assignee=old_assignee,
            new_assignee=new_assignee,
            created_by=user,
            ip_address=ip_address
        )
    
    @classmethod
    def log_resolution(cls, ticket, user=None, ip_address=None):
        """Log ticket resolution"""
        return cls.objects.create(
            ticket=ticket,
            action=cls.ActionType.RESOLVED,
            created_by=user,
            ip_address=ip_address
        )
    
    @classmethod
    def log_closing(cls, ticket, user=None, ip_address=None):
        """Log ticket closing"""
        return cls.objects.create(
            ticket=ticket,
            action=cls.ActionType.CLOSED,
            created_by=user,
            ip_address=ip_address
        )