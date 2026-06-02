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

    #  customer is NOT registered user
    customer_name = models.CharField(max_length=255, default='Unknown')
    customer_contact = models.CharField(max_length=100, default='Not Provided')

    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='WEB')

    title = models.CharField(max_length=255, default='Untitled Ticket')
    description = models.TextField(default='No description provided')

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    assigned_to = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)