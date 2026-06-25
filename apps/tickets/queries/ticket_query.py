from django.db.models import Q
from ..models import Ticket


class TicketQuery:
    """Filter and role‑based queryset builder."""

    def __init__(self, request):
        self.request = request

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Ticket.objects.none()

        role = self._get_user_role(user)
        qs = Ticket.objects.select_related(
            "team", "assigned_to", "assigned_by", "customer", "street"
        ).prefetch_related("attachments", "histories").order_by("-id")

        # =========================
        # ADMIN - Can see all tickets
        # =========================
        if role == "ADMIN":
            return qs

        # =========================
        # TEAM_LEAD - Can see tickets assigned to their team
        # =========================
        elif role == "TEAM_LEAD":
            if user.team_id:
                return qs.filter(
                    Q(team_id=user.team_id) |  # Tickets assigned to their team
                    Q(assigned_to__team_id=user.team_id)  # Tickets assigned to agents in their team
                )
            return Ticket.objects.none()

        # =========================
        # AGENT - Can see tickets assigned to them OR unassigned tickets
        # =========================
        elif role == "AGENT":
            return qs.filter(
                Q(assigned_to=user) |  # Assigned to this agent
                Q(assigned_to__isnull=True) |  # Unassigned tickets
                Q(team_id=user.team_id)  # Tickets assigned to their team
            )

        # =========================
        # SUPPORT - Same as AGENT (can see their tickets + unassigned + team tickets)
        # =========================
        elif role == "SUPPORT":
            return qs.filter(
                Q(assigned_to=user) |
                Q(assigned_to__isnull=True) |
                Q(team_id=user.team_id)
            )

        # =========================
        # MANAGER - Can see tickets assigned to their team
        # =========================
        elif role == "MANAGER":
            if user.team_id:
                return qs.filter(
                    Q(team_id=user.team_id) |
                    Q(assigned_to__team_id=user.team_id)
                )
            return Ticket.objects.none()

        # =========================
        # DEFAULT - No access
        # =========================
        return Ticket.objects.none()

    def apply_filters(self, queryset):
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
        
        # My tickets filter
        if params.get("my") == "true":
            queryset = queryset.filter(assigned_to=self.request.user)
        
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
        
        # Filter by role (for superusers)
        role = params.get("role")
        if role:
            queryset = queryset.filter(assigned_to__role_name=role.upper())
        
        return queryset

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