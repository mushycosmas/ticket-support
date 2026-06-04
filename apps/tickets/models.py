from django.db import models


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
    # LOCATION (ONLY STREET)
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

    def __str__(self):
        return f"{self.title} ({self.status})"


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