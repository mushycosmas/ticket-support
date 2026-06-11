from django.db.models import Q
from ..models import Ticket


class TicketQuery:
    def __init__(self, request):
        self.request = request

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Ticket.objects.none()

        qs = Ticket.objects.select_related(
            "team", "assigned_to", "customer", "street"
        ).prefetch_related("attachments", "histories").order_by("-id")

        role = self._get_role(user)

        if role == "ADMIN":
            return qs

        if role == "TEAM_LEAD":
            return qs.filter(team_id=user.team_id)

        if role == "AGENT":
            return qs.filter(Q(assigned_to=user) | Q(assigned_to__isnull=True))

        if role == "MANAGER":
            return qs.filter(team_id=user.team_id)

        return Ticket.objects.none()

    def apply_filters(self, qs):
        params = self.request.query_params

        if params.get("filter") == "my":
            qs = qs.filter(assigned_to=self.request.user)

        if params.get("status"):
            qs = qs.filter(status=params["status"].upper())

        if params.get("priority"):
            qs = qs.filter(priority=params["priority"].upper())

        if params.get("search"):
            qs = qs.filter(title__icontains=params["search"])

        return qs

    def _get_role(self, user):
        if hasattr(user, "role") and user.role:
            return getattr(user.role, "name", str(user.role)).upper()
        return None