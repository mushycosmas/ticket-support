from django.contrib.auth.models import AbstractUser
from django.db import models


# 👥 TEAM MODEL
class Team(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# 👤 USER MODEL
class User(AbstractUser):

    ROLE_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('AGENT', 'Agent'),
        ('TEAM_LEAD', 'Team Lead'),
        ('QA', 'QA'),
        ('MANAGER', 'Manager'),
        ('ADMIN', 'Admin'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='AGENT'
    )

    phone = models.CharField(max_length=20, null=True, blank=True)

    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members"
    )

    created_at = models.DateTimeField(auto_now_add=True)