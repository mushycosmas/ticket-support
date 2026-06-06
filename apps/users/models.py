from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone


# 👥 TEAM MODEL
class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Team Lead reference (optional, can be set separately)
    lead = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teams_leading"
    )
    
    # Members (Many-to-Many relationship)
    members = models.ManyToManyField(
        'User',
        related_name="teams",
        blank=True
    )
    
    # Timestamps
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


# 👤 USER MODEL
class User(AbstractUser):
    
    ROLE_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('AGENT', 'Agent'),
        ('TEAM_LEAD', 'Team Lead'),
        ('QA_ANALYST', 'QA Analyst'),
        ('MANAGER', 'Manager'),
        ('ADMIN', 'Admin'),
    ]
    
    # Basic Information
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='AGENT'
    )
    
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in international format (+1234567890)"
            )
        ]
    )
    
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(message="Enter a valid email address")]
    )
    
    # Profile Information
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    
    bio = models.TextField(max_length=500, blank=True, null=True)
    
    # Assignment
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_members"
    )
    
    # Availability Status (for agents)
    is_available = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    def save(self, *args, **kwargs):
        # Update last_activity on save
        if not self.last_activity:
            self.last_activity = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return self.get_full_name() or self.username
    
    @property
    def role_display(self):
        """Return the role display name."""
        return dict(self.ROLE_CHOICES).get(self.role, self.role)
    
    @property
    def total_tickets_assigned(self):
        """Get total tickets assigned to this user."""
        from apps.tickets.models import Ticket
        return Ticket.objects.filter(assigned_to=self).count()
    
    @property
    def open_tickets(self):
        """Get open tickets assigned to this user."""
        from apps.tickets.models import Ticket
        return Ticket.objects.filter(assigned_to=self, status='OPEN').count()
    
    @property
    def in_progress_tickets(self):
        """Get in-progress tickets assigned to this user."""
        from apps.tickets.models import Ticket
        return Ticket.objects.filter(assigned_to=self, status='IN_PROGRESS').count()
    
    @property
    def resolved_tickets(self):
        """Get resolved tickets assigned to this user."""
        from apps.tickets.models import Ticket
        return Ticket.objects.filter(assigned_to=self, status='RESOLVED').count()
    
    def update_last_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def is_team_lead(self):
        """Check if user is a team lead."""
        return self.role == 'TEAM_LEAD'
    
    def is_agent(self):
        """Check if user is an agent."""
        return self.role == 'AGENT'
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'ADMIN' or self.is_superuser
    
    def can_assign_tickets(self):
        """Check if user can assign tickets."""
        return self.role in ['ADMIN', 'TEAM_LEAD', 'MANAGER']
    
    def can_view_all_tickets(self):
        """Check if user can view all tickets."""
        return self.role in ['ADMIN', 'MANAGER']