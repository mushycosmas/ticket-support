# apps/tickets/queries/ticket_query.py

from django.db.models import Q
from ..models import Ticket


class TicketQuery:
    """Filter and role‑based queryset builder."""

    def __init__(self, request):
        self.request = request

    def _get_user_role(self, user):
        """Extract user role consistently."""
        if not user:
            return None
        
        # Check role attribute (ForeignKey or CharField)
        if hasattr(user, "role") and user.role:
            if hasattr(user.role, "name"):
                return user.role.name.upper()
            elif isinstance(user.role, str):
                return user.role.upper()
        
        # Check role_name attribute
        if hasattr(user, "role_name") and user.role_name:
            return user.role_name.upper()
        
        return None

    def _get_user_team_ids(self, user):
        """
        Get all team IDs for a user.
        Handles different relationship names.
        """
        team_ids = []
        
        # Check for leading_teams (if user is a lead)
        if hasattr(user, 'leading_teams'):
            team_ids.extend(
                user.leading_teams.values_list('id', flat=True)
            )
        
        # Check for teams (many-to-many)
        if hasattr(user, 'teams'):
            team_ids.extend(
                user.teams.values_list('id', flat=True)
            )
        
        # Remove duplicates
        return list(set(team_ids))

    def get_queryset(self):
        """
        Role-based ticket visibility.

        ADMIN
            - Can view all tickets.

        TEAM_LEAD
            - Can view tickets belonging to every team they lead.
            - Can also view tickets assigned to members of those teams.
            - Can always view tickets assigned to themselves.

        MANAGER
            - Can view tickets belonging to teams they are members of.

        AGENT / SUPPORT
            - Can only view tickets assigned to themselves.
        """
        user = self.request.user

        if not user or not user.is_authenticated:
            return Ticket.objects.none()

        role = self._get_user_role(user)

        # Base queryset with select_related for performance
        qs = (
            Ticket.objects
            .select_related(
                "team",
                "assigned_to",
                "assigned_by",
                "customer",
                "street",
                "category",
                "channel"
            )
            .order_by("-created_at")
        )

        # Only prefetch related fields that exist
        if hasattr(Ticket, 'attachments'):
            qs = qs.prefetch_related('attachments')
        
        # Check if history relation exists (try different possible names)
        if hasattr(Ticket, 'history'):
            qs = qs.prefetch_related('history')
        elif hasattr(Ticket, 'histories'):
            qs = qs.prefetch_related('histories')

        # =====================================
        # ADMIN
        # =====================================
        if role == "ADMIN" or user.is_superuser:
            return qs

        # =====================================
        # TEAM LEAD
        # =====================================
        if role == "TEAM_LEAD":
            # Get all team IDs where user is a lead OR member
            team_ids = self._get_user_team_ids(user)

            if not team_ids:
                # If not in any team, only show tickets assigned to them
                return qs.filter(assigned_to=user)

            # Get all users that are members of these teams
            from apps.users.models import User
            team_member_ids = User.objects.filter(
                teams__id__in=team_ids
            ).values_list('id', flat=True)

            return (
                qs.filter(
                    Q(team_id__in=team_ids) |           # Tickets in their teams
                    Q(assigned_to__in=team_member_ids) | # Tickets assigned to team members
                    Q(assigned_to=user)                 # Tickets assigned to themselves
                )
                .distinct()
            )

        # =====================================
        # MANAGER
        # =====================================
        if role == "MANAGER":
            team_ids = []
            
            if hasattr(user, 'teams'):
                team_ids = list(user.teams.values_list('id', flat=True))

            if not team_ids:
                return Ticket.objects.none()

            # Get all users that are members of these teams
            from apps.users.models import User
            team_member_ids = User.objects.filter(
                teams__id__in=team_ids
            ).values_list('id', flat=True)

            return (
                qs.filter(
                    Q(team_id__in=team_ids) |
                    Q(assigned_to__in=team_member_ids)
                )
                .distinct()
            )

        # =====================================
        # AGENT
        # =====================================
        if role == "AGENT":
            return qs.filter(assigned_to=user)

        # =====================================
        # SUPPORT
        # =====================================
        if role == "SUPPORT":
            return qs.filter(assigned_to=user)

        # =====================================
        # CUSTOMER
        # =====================================
        if role == "CUSTOMER":
            return qs.filter(created_by=user)

        # =====================================
        # DEFAULT
        # =====================================
        return Ticket.objects.none()

    def apply_filters(self, queryset):
        """
        Apply additional filters from request parameters.
        """
        params = self.request.query_params
        
        # Status filter
        status = params.get("status")
        if status:
            queryset = queryset.filter(status=status.upper())
        
        # Priority filter
        priority = params.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority.upper())
        
        # Search filter
        search = params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(ticket_number__icontains=search) |
                Q(description__icontains=search) |
                Q(customer__full_name__icontains=search) |
                Q(customer__email__icontains=search)
            )
        
        # My tickets filter (assigned to current user)
        my_tickets = params.get("my")
        if my_tickets and my_tickets.lower() == "true":
            queryset = queryset.filter(assigned_to=self.request.user)
        
        # My team tickets filter (tickets in user's teams)
        my_team = params.get("my_team")
        if my_team and my_team.lower() == "true":
            team_ids = self._get_user_team_ids(self.request.user)
            if team_ids:
                queryset = queryset.filter(team_id__in=team_ids)
        
        # Unassigned tickets filter
        unassigned = params.get("unassigned")
        if unassigned and unassigned.lower() == "true":
            queryset = queryset.filter(assigned_to__isnull=True)
        
        # Team filter (for admins/managers)
        team_id = params.get("team_id")
        if team_id:
            try:
                queryset = queryset.filter(team_id=int(team_id))
            except (TypeError, ValueError):
                pass
        
        # Agent filter (for admins/managers)
        assigned_to = params.get("assigned_to")
        if assigned_to:
            try:
                queryset = queryset.filter(assigned_to_id=int(assigned_to))
            except (TypeError, ValueError):
                pass
        
        # Date range filter
        from_date = params.get("from_date")
        to_date = params.get("to_date")
        if from_date:
            queryset = queryset.filter(created_at__gte=from_date)
        if to_date:
            queryset = queryset.filter(created_at__lte=to_date)
        
        # Priority filter (alternative)
        priority_high = params.get("priority_high")
        if priority_high and priority_high.lower() == "true":
            queryset = queryset.filter(priority="HIGH")
        
        # Category filter
        category = params.get("category")
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Channel filter
        channel = params.get("channel")
        if channel:
            queryset = queryset.filter(channel_id=channel)
        
        # Filter by role (for superusers/admin)
        role = params.get("role")
        if role:
            queryset = queryset.filter(assigned_to__role_name=role.upper())
        
        return queryset

    def get_stats(self, queryset=None):
        """
        Get ticket statistics for the current user.
        """
        if queryset is None:
            queryset = self.get_queryset()
        
        return {
            "total": queryset.count(),
            "open": queryset.filter(status="OPEN").count(),
            "assigned": queryset.filter(status="ASSIGNED").count(),
            "in_progress": queryset.filter(status="IN_PROGRESS").count(),
            "resolved": queryset.filter(status="RESOLVED").count(),
            "closed": queryset.filter(status="CLOSED").count(),
            "high_priority": queryset.filter(priority="HIGH").count(),
            "critical_priority": queryset.filter(priority="CRITICAL").count(),
            "unassigned": queryset.filter(assigned_to__isnull=True).count(),
        }

    def get_summary(self, queryset=None):
        """
        Get a summary of tickets for dashboard.
        """
        if queryset is None:
            queryset = self.get_queryset()
        
        return {
            "total": queryset.count(),
            "by_status": {
                "OPEN": queryset.filter(status="OPEN").count(),
                "ASSIGNED": queryset.filter(status="ASSIGNED").count(),
                "IN_PROGRESS": queryset.filter(status="IN_PROGRESS").count(),
                "RESOLVED": queryset.filter(status="RESOLVED").count(),
                "CLOSED": queryset.filter(status="CLOSED").count(),
            },
            "by_priority": {
                "LOW": queryset.filter(priority="LOW").count(),
                "MEDIUM": queryset.filter(priority="MEDIUM").count(),
                "HIGH": queryset.filter(priority="HIGH").count(),
                "CRITICAL": queryset.filter(priority="CRITICAL").count(),
            },
            "by_category": self._get_category_counts(queryset),
            "by_team": self._get_team_counts(queryset),
        }

    def _get_user_team_ids(self, user):
        """
        Get all team IDs for a user.
        Handles different relationship names.
        """
        team_ids = []
        
        # Check for leading_teams (if user is a lead)
        if hasattr(user, 'leading_teams'):
            team_ids.extend(
                user.leading_teams.values_list('id', flat=True)
            )
        
        # Check for teams (many-to-many)
        if hasattr(user, 'teams'):
            team_ids.extend(
                user.teams.values_list('id', flat=True)
            )
        
        # Remove duplicates
        return list(set(team_ids))

    def get_assigned_tickets(self):
        """Get tickets assigned to the current user."""
        if not self.request.user or not self.request.user.is_authenticated:
            return Ticket.objects.none()
        
        return Ticket.objects.filter(assigned_to=self.request.user)

    def get_created_tickets(self):
        """Get tickets created by the current user."""
        if not self.request.user or not self.request.user.is_authenticated:
            return Ticket.objects.none()
        
        return Ticket.objects.filter(created_by=self.request.user)

    def get_team_tickets(self, team_id=None):
        """Get tickets for a specific team or all teams the user belongs to."""
        queryset = self.get_queryset()
        
        if team_id:
            return queryset.filter(team_id=team_id)
        
        return queryset

    def get_unassigned_tickets(self):
        """Get unassigned tickets (for admins/managers/team leads)."""
        queryset = self.get_queryset()
        return queryset.filter(assigned_to__isnull=True)

    def _get_team_counts(self, queryset):
        """Get ticket counts by team."""
        try:
            from apps.users.models import Team
            
            teams = Team.objects.all()
            counts = {}
            for team in teams:
                count = queryset.filter(team=team).count()
                if count > 0:
                    counts[team.name] = count
            return counts
        except ImportError:
            return {}

    def _get_category_counts(self, queryset):
        """Get ticket counts by category."""
        try:
            from apps.categories.models import Category
            
            categories = Category.objects.all()
            counts = {}
            for category in categories:
                count = queryset.filter(category=category).count()
                if count > 0:
                    counts[category.name] = count
            return counts
        except ImportError:
            return {}

    def get_activity_timeline(self, limit=10):
        """Get recent ticket activity for dashboard."""
        queryset = self.get_queryset()
        return queryset.order_by('-updated_at')[:limit]

    def get_ticket_by_number(self, ticket_number):
        """Get a ticket by its ticket number."""
        return self.get_queryset().filter(ticket_number=ticket_number).first()

    def get_tickets_for_export(self):
        """Get tickets formatted for export."""
        queryset = self.get_queryset()
        return queryset.values(
            'id',
            'ticket_number',
            'title',
            'status',
            'priority',
            'created_at',
            'updated_at',
            'customer__full_name',
            'customer__email',
            'assigned_to__username',
            'team__name',
            'category__name',
            'channel__name'
        )