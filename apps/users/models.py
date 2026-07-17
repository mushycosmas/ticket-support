# apps/users/models.py

from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone

from apps.roles.models import Role


# ======================
# 👥 TEAM MODEL
# ======================
class Team(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    # One user can lead many teams
    lead = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leading_teams'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

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
# 👤 USER MODEL
# ======================
class User(AbstractUser):

    # ======================
    # ROLE
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

    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True
    )


    # ======================
    # TEAMS
    # User can belong to many teams
    # ======================
    teams = models.ManyToManyField(
        Team,
        blank=True,
        related_name='members'
    )


    # ======================
    # STATUS
    # ======================
    is_available = models.BooleanField(
        default=True
    )


    # ======================
    # PASSWORD TRACKING
    # ======================
    is_default_password = models.BooleanField(
        default=True,
        help_text="Indicates if user is still using the default password"
    )

    last_password_change = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the last password change"
    )


    # ======================
    # TIMESTAMPS
    # ======================
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    last_activity = models.DateTimeField(
        null=True,
        blank=True
    )


    # ======================
    # META
    # ======================
    class Meta:
        ordering = ['-date_joined']
        verbose_name = "User"
        verbose_name_plural = "Users"


    def __str__(self):
        return self.get_full_name() or self.username


    # ======================
    # SAVE
    # ======================
    def save(self, *args, **kwargs):

        if not self.last_activity:
            self.last_activity = timezone.now()

        super().save(*args, **kwargs)


    # ======================
    # PASSWORD TRACKING
    # ======================
    def set_password(self, raw_password):

        super().set_password(raw_password)

        self.is_default_password = False
        self.last_password_change = timezone.now()

        if self.pk:
            self.save(
                update_fields=[
                    'password',
                    'is_default_password',
                    'last_password_change'
                ]
            )


    def is_using_default_password(self):
        return self.is_default_password


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
    def team_names(self):
        """
        Return all teams assigned to user
        """
        return list(
            self.teams.values_list(
                'name',
                flat=True
            )
        )


    @property
    def needs_password_change(self):
        return self.is_default_password


    # ======================
    # PERMISSIONS
    # ======================
    def get_role_permissions(self):

        if self.role:
            return self.role.permissions.all()

        return Permission.objects.none()


    def has_role_permission(self, codename):

        return self.get_role_permissions().filter(
            codename=codename
        ).exists()


    # ======================
    # TICKET STATISTICS
    # ======================
    @property
    def total_tickets_assigned(self):

        from apps.tickets.models import Ticket

        return Ticket.objects.filter(
            assigned_to=self
        ).count()


    @property
    def open_tickets(self):

        from apps.tickets.models import Ticket

        return Ticket.objects.filter(
            assigned_to=self,
            status='OPEN'
        ).count()


    @property
    def in_progress_tickets(self):

        from apps.tickets.models import Ticket

        return Ticket.objects.filter(
            assigned_to=self,
            status='IN_PROGRESS'
        ).count()


    @property
    def resolved_tickets(self):

        from apps.tickets.models import Ticket

        return Ticket.objects.filter(
            assigned_to=self,
            status='RESOLVED'
        ).count()


    # ======================
    # ACTIVITY
    # ======================
    def update_last_activity(self):

        self.last_activity = timezone.now()

        self.save(
            update_fields=[
                'last_activity'
            ]
        )