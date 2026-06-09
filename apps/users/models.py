from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone

from apps.roles.models import Role


# ======================
# 👥 TEAM MODEL
# ======================
class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    lead = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leading_teams'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()


# ======================
# 👤 USER MODEL (RBAC CLEAN)
# ======================
class User(AbstractUser):

    # ======================
    # ROLE (FROM ROLE TABLE)
    # ======================
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )
    rank = models.CharField(
            max_length=50,
            null=True,
            blank=True
     )
    # ======================
    # CONTACT
    # ======================
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()]
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone must be in international format"
            )
        ]
    )

    # ======================
    # PROFILE
    # ======================
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )

    bio = models.TextField(max_length=500, blank=True, null=True)

    # ======================
    # TEAM
    # ======================
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )

    # ======================
    # STATUS
    # ======================
    is_available = models.BooleanField(default=True)

    # ======================
    # TIMESTAMPS
    # ======================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_joined']
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.get_full_name() or self.username

    # ======================
    # SAVE OVERRIDE
    # ======================
    def save(self, *args, **kwargs):
        if not self.last_activity:
            self.last_activity = timezone.now()
        super().save(*args, **kwargs)

    # ======================
    # PROPERTIES
    # ======================
    @property
    def full_name(self):
        return self.get_full_name() or self.username

    @property
    def role_name(self):
        return self.role.name if self.role else None

    @property
    def team_name(self):
        return self.team.name if self.team else None

    # ======================
    # PERMISSIONS (DJANGO NATIVE)
    # ======================
    def get_role_permissions(self):
        """
        Returns permissions from Role (many-to-many)
        """
        if self.role:
            return self.role.permissions.all()
        return Permission.objects.none()

    def has_role_permission(self, codename):
        """
        Check permission from Role
        """
        return self.get_role_permissions().filter(codename=codename).exists()

    # ======================
    # TICKET STATS
    # ======================
    @property
    def total_tickets_assigned(self):
        from apps.tickets.models import Ticket
        return Ticket.objects.filter(assigned_to=self).count()

    @property
    def open_tickets(self):
        from apps.tickets.models import Ticket
        return Ticket.objects.filter(assigned_to=self, status='OPEN').count()

    @property
    def in_progress_tickets(self):
        from apps.tickets.models import Ticket
        return Ticket.objects.filter(assigned_to=self, status='IN_PROGRESS').count()

    @property
    def resolved_tickets(self):
        from apps.tickets.models import Ticket
        return Ticket.objects.filter(assigned_to=self, status='RESOLVED').count()

    # ======================
    # ACTIVITY
    # ======================
    def update_last_activity(self):
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])