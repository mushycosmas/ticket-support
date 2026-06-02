from django.db import models


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
    # CUSTOMER (NO LOGIN)
    # =====================
    customer_name = models.CharField(max_length=255, default='Unknown')
    customer_contact = models.CharField(max_length=100, default='Not Provided')

    # =====================
    # TICKET INFO
    # =====================
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='WEB')
    title = models.CharField(max_length=255)
    description = models.TextField()

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    # =====================
    # WORKFLOW (IMPORTANT FIX)
    # =====================

    # 1. Ticket goes to TEAM first
    team = models.ForeignKey(
        "users.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets"
    )

    # 2. Then assigned to AGENT
    assigned_to = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"