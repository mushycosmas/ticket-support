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

    def get_queryset(self):
        """
        Get filtered queryset based on user role.
        
        Role-based access:
        - ADMIN: All tickets
        - TEAM_LEAD: Tickets in their team
        - AGENT/SUPPORT: ONLY tickets assigned to them
        - MANAGER: Tickets in their team
        - Default: No access
        """
        user = self.request.user
        
        if not user or not user.is_authenticated:
            return Ticket.objects.none()

        role = self._get_user_role(user)
        
        # Base queryset with related fields
        qs = Ticket.objects.select_related(
            "team", "assigned_to", "assigned_by", "customer", "street"
        ).prefetch_related("attachments", "histories").order_by("-id")

        # =========================
        # ADMIN - Can see all tickets
        # =========================
        if role == "ADMIN":
            return qs

        # =========================
        # TEAM_LEAD - Can see tickets in their team
        # =========================
        elif role == "TEAM_LEAD":
            if user.team_id:
                return qs.filter(
                    Q(team_id=user.team_id) |
                    Q(assigned_to__team_id=user.team_id) |
                    Q(assigned_to=user)
                ).distinct()
            return Ticket.objects.none()

        # =========================
        # AGENT - ONLY tickets assigned to them
        # =========================
        elif role == "AGENT":
            # ✅ Agents only see tickets assigned to them
            return qs.filter(assigned_to=user)

        # =========================
        # SUPPORT - ONLY tickets assigned to them
        # =========================
        elif role == "SUPPORT":
            # ✅ Support only see tickets assigned to them
            return qs.filter(assigned_to=user)

        # =========================
        # MANAGER - Can see tickets in their team
        # =========================
        elif role == "MANAGER":
            if user.team_id:
                return qs.filter(
                    Q(team_id=user.team_id) |
                    Q(assigned_to__team_id=user.team_id)
                ).distinct()
            return Ticket.objects.none()

        # =========================
        # DEFAULT - No access
        # =========================
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
        }