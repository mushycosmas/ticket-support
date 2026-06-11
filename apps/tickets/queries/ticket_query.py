from django.db.models import Q
from ..models import Ticket   # ✅ add this line


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

        if role == "ADMIN":
            return qs
        elif role == "TEAM_LEAD":
            return qs.filter(team_id=user.team_id)
        elif role == "AGENT":
            return qs.filter(Q(assigned_to=user) | Q(assigned_to__isnull=True))
        elif role == "MANAGER":
            return qs.filter(team_id=user.team_id)
        return Ticket.objects.none()

    def apply_filters(self, queryset):
        params = self.request.query_params
        status = params.get("status")
        if status:
            queryset = queryset.filter(status=status.upper())
        priority = params.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority.upper())
        search = params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search)
        if params.get("my") == "true":
            queryset = queryset.filter(assigned_to=self.request.user)
        return queryset

    def _get_user_role(self, user):
        if hasattr(user, "role") and user.role:
            if hasattr(user.role, "name"):
                return user.role.name.upper()
            elif isinstance(user.role, str):
                return user.role.upper()
        if hasattr(user, "role_name") and user.role_name:
            return user.role_name.upper()
        return None