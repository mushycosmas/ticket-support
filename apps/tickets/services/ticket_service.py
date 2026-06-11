import uuid
from django.contrib.auth import get_user_model

from ..models import Ticket, Customer, TicketHistory

User = get_user_model()


# =========================
# WORKFLOW LAYER
# =========================
class TicketWorkflow:

    @staticmethod
    def can_assign(ticket):
        return ticket.status == "OPEN"

    @staticmethod
    def assign(ticket, user):
        ticket.status = "ASSIGNED"
        ticket.assigned_to = user
        ticket.save()
        return ticket

    @staticmethod
    def start_progress(ticket):
        if ticket.status == "ASSIGNED":
            ticket.status = "IN_PROGRESS"
            ticket.save()
        return ticket

    @staticmethod
    def resolve(ticket):
        ticket.status = "RESOLVED"
        ticket.save()
        return ticket

    @staticmethod
    def close(ticket):
        ticket.status = "CLOSED"
        ticket.save()
        return ticket


# =========================
# SERVICE LAYER
# =========================
class TicketService:

    @staticmethod
    def safe_int(value):
        try:
            if value in [None, "", "null", "undefined"]:
                return None
            return int(value)
        except (TypeError, ValueError):
            return None

    # =========================
    # CREATE TICKET
    # =========================
    @staticmethod
    def create_ticket(request):
        data = request.data

        email = data.get("customer_email")
        phone = data.get("customer_phone")
        name = data.get("customer_name")

        # =========================
        # CUSTOMER
        # =========================
        customer = None
        if email or phone:
            customer, _ = Customer.get_or_create_customer(
                email=email,
                phone=phone,
                full_name=name,

                # FIXED FIELD MAPPING
                nida_number=data.get("customer_nida"),
                gender=data.get("customer_gender"),
            )

        # =========================
        # SAFE FK HANDLING (IMPORTANT FIX HERE)
        # =========================
        category_id = TicketService.safe_int(
            data.get("category_id") or data.get("category")
        )

        channel_id = TicketService.safe_int(
            data.get("channel_id") or data.get("channel")
        )

        street_id = TicketService.safe_int(data.get("street_id"))
        team_id = TicketService.safe_int(data.get("team"))
        assigned_to_id = TicketService.safe_int(data.get("assigned_to"))
        assigned_by_id = TicketService.safe_int(data.get("assigned_by"))

        # =========================
        # CREATE TICKET
        # =========================
        ticket = Ticket.objects.create(
            ticket_number=f"TKT-{uuid.uuid4().hex[:8].upper()}",
            title=data.get("title"),
            description=data.get("description", ""),
            priority=data.get("priority", "MEDIUM"),
            status="OPEN",

            category_id=category_id,
            channel_id=channel_id,
            street_id=street_id,

            customer=customer,
        )

        # =========================
        # RELATIONSHIPS
        # =========================
        TicketService.assign_relationships(
            ticket,
            assigned_to_id,
            assigned_by_id,
            team_id,
            request
        )

        # =========================
        # HISTORY
        # =========================
        TicketHistory.objects.create(
            ticket=ticket,
            action="CREATED",
            created_by=request.user if request.user.is_authenticated else None,
        )

        return ticket

    # =========================
    # ASSIGN RELATIONSHIPS
    # =========================
    @staticmethod
    def assign_relationships(ticket, assigned_to_id, assigned_by_id, team_id, request):

        # ASSIGNED TO
        if assigned_to_id:
            try:
                user = User.objects.get(id=assigned_to_id)
                ticket.assigned_to = user
                ticket.status = "IN_PROGRESS"
            except User.DoesNotExist:
                pass

        # ASSIGNED BY
        if assigned_by_id:
            try:
                ticket.assigned_by = User.objects.get(id=assigned_by_id)
            except User.DoesNotExist:
                pass
        elif request.user.is_authenticated:
            ticket.assigned_by = request.user

        # TEAM
        if team_id:
            ticket.team_id = team_id

        ticket.save()