import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied

from ..models import Ticket, Customer, TicketHistory
from apps.users.models import Team

User = get_user_model()

# =========================
# CONSTANTS
# =========================
ALLOWED_ASSIGNEE_ROLES = ["AGENT", "SUPPORT", "ADMIN", "TEAM_LEAD"]


# =========================
# WORKFLOW LAYER (state machine)
# =========================
class TicketWorkflow:
    """Valid transitions for ticket status."""

    @staticmethod
    def assign(ticket, user):
        # No status check – allow assignment anytime
        ticket.status = "ASSIGNED"
        ticket.assigned_to = user
        ticket.save()
        return ticket

    @staticmethod
    def start_progress(ticket):
        if ticket.status != "ASSIGNED":
            raise ValueError(f"Cannot start progress from status '{ticket.status}'")
        ticket.status = "IN_PROGRESS"
        ticket.save()
        return ticket

    @staticmethod
    def resolve(ticket):
        if ticket.status not in ("IN_PROGRESS", "ASSIGNED", "OPEN"):
            raise ValueError(f"Cannot resolve ticket with status '{ticket.status}'")
        ticket.status = "RESOLVED"
        ticket.resolved_at = timezone.now()
        ticket.save()
        return ticket

    @staticmethod
    def close(ticket):
        if ticket.status == "CLOSED":
            return ticket
        ticket.status = "CLOSED"
        ticket.save()
        return ticket

    @staticmethod
    def reopen(ticket):
        if ticket.status not in ("CLOSED", "RESOLVED"):
            raise ValueError(f"Cannot reopen ticket with status '{ticket.status}'")
        ticket.status = "OPEN"
        ticket.resolved_at = None
        ticket.save()
        return ticket


# =========================
# SERVICE LAYER (business logic)
# =========================
class TicketService:
    """Handles all ticket operations and delegates state changes to workflow."""

    @staticmethod
    def safe_int(value):
        """Convert to int safely, return None for invalid input."""
        if value in (None, "", "null", "undefined"):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _get_user_role(user):
        """Extract user role from various possible field structures."""
        if not user:
            return None
        
        if hasattr(user, "role") and user.role:
            if hasattr(user.role, "name"):
                return user.role.name.upper()
            return str(user.role).upper()
        elif hasattr(user, "role_name") and user.role_name:
            return user.role_name.upper()
        
        return None

    @staticmethod
    def _is_admin(user):
        """Check if user has admin role."""
        role = TicketService._get_user_role(user)
        return role == "ADMIN"

    @staticmethod
    def _is_team_lead(user):
        """Check if user has team lead role."""
        role = TicketService._get_user_role(user)
        return role == "TEAM_LEAD"

    # ---------- CREATE ----------
    @staticmethod
    @transaction.atomic
    def create_ticket(request):
        data = request.data

        # Customer handling
        email = data.get("customer_email")
        phone = data.get("customer_phone")
        name = data.get("customer_name")

        customer = None
        if email or phone:
            customer, _ = Customer.get_or_create_customer(
                email=email,
                phone=phone,
                full_name=name,
                nida_number=data.get("customer_nida"),
                gender=data.get("customer_gender"),
                created_by_id=request.user.id if request.user.is_authenticated else None,
            )

        # Foreign keys
        category_id = TicketService.safe_int(data.get("category_id") or data.get("category"))
        channel_id = TicketService.safe_int(data.get("channel_id") or data.get("channel"))
        street_id = TicketService.safe_int(data.get("street_id"))
        team_id = TicketService.safe_int(data.get("team"))
        assigned_to_id = TicketService.safe_int(data.get("assigned_to"))
        assigned_by_id = TicketService.safe_int(data.get("assigned_by"))
        template_id = TicketService.safe_int(data.get("template"))

        # Create ticket
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
            template_id=template_id,
        )

        # Assign relationships
        TicketService._assign_relationships(ticket, assigned_to_id, assigned_by_id, team_id, request)

        # History (with metadata)
        TicketHistory.objects.create(
            ticket=ticket,
            action="CREATED",
            created_by=request.user if request.user.is_authenticated else None,
            metadata={
                "title": ticket.title,
                "description": ticket.description,
                "street_id": street_id,
                "assigned_to": assigned_to_id,
                "assigned_by": assigned_by_id,
                "team_id": team_id,
                "template_id": template_id,
            }
        )

        return ticket

    @staticmethod
    def _assign_relationships(ticket, assigned_to_id, assigned_by_id, team_id, request):
        if assigned_to_id:
            user = User.objects.filter(id=assigned_to_id).first()
            if user:
                ticket.assigned_to = user
                ticket.status = "IN_PROGRESS"
        if assigned_by_id:
            by_user = User.objects.filter(id=assigned_by_id).first()
            if by_user:
                ticket.assigned_by = by_user
        elif request.user.is_authenticated:
            ticket.assigned_by = request.user
        if team_id:
            ticket.team_id = team_id
        ticket.save(update_fields=["assigned_to", "assigned_by", "team_id", "status"])

    # ---------- STATE CHANGES (with comment support) ----------
    @staticmethod
    def resolve(ticket, request, comment=""):
        old_status = ticket.status
        try:
            ticket = TicketWorkflow.resolve(ticket)
        except ValueError as e:
            raise ValueError(str(e))
        TicketHistory.objects.create(
            ticket=ticket,
            action="RESOLVED",
            comment=comment,
            old_status=old_status,
            new_status=ticket.status,
            created_by=request.user if request.user.is_authenticated else None,
            metadata={"comment": comment}
        )
        return ticket

    @staticmethod
    def close(ticket, request, comment=""):
        old_status = ticket.status
        ticket = TicketWorkflow.close(ticket)
        TicketHistory.objects.create(
            ticket=ticket,
            action="CLOSED",
            comment=comment,
            old_status=old_status,
            new_status=ticket.status,
            created_by=request.user if request.user.is_authenticated else None,
            metadata={"comment": comment}
        )
        return ticket

    @staticmethod
    def reopen(ticket, request, comment=""):
        old_status = ticket.status
        try:
            ticket = TicketWorkflow.reopen(ticket)
        except ValueError as e:
            raise ValueError(str(e))
        TicketHistory.objects.create(
            ticket=ticket,
            action="REOPENED",
            comment=comment,
            old_status=old_status,
            new_status=ticket.status,
            created_by=request.user if request.user.is_authenticated else None,
            metadata={"comment": comment}
        )
        return ticket

    # ---------- ASSIGN (supports both agent and team - keeps both) ----------
    @staticmethod
    def assign(ticket, request):
        assign_type = request.data.get("type")
        obj_id = request.data.get("id")

        if not assign_type or not obj_id:
            raise ValidationError("type and id are required")

        old_team = ticket.team
        old_assignee = ticket.assigned_to
        requesting_user = request.user if request.user.is_authenticated else None
        is_admin = TicketService._is_admin(requesting_user)
        is_team_lead = TicketService._is_team_lead(requesting_user)

        # ======================
        # TEAM ASSIGNMENT
        # ======================
        if assign_type == "team":
            try:
                team = Team.objects.get(id=obj_id)
            except Team.DoesNotExist:
                raise ValidationError("Team not found")

            # Check permissions for non-admins
            if not is_admin and not is_team_lead:
                raise PermissionDenied("Only admins and team leads can assign to teams")

            # ✅ KEEP existing agent assignment - DO NOT clear assigned_to
            ticket.team = team
            # DO NOT: ticket.assigned_to = None  ← Keep the agent!
            ticket.assigned_by = requesting_user
            ticket.status = "ASSIGNED"
            ticket.save()

            # History (FULL TRACE)
            assigned_to_info = f" (with assignee {old_assignee})" if old_assignee else ""
            TicketHistory.objects.create(
                ticket=ticket,
                action="ASSIGNED",
                comment=f"Assigned to team {team.name}{assigned_to_info}",
                old_team=old_team,
                new_team=team,
                old_assignee=old_assignee,
                new_assignee=old_assignee,  # Keep the same assignee
                created_by=requesting_user,
                metadata={
                    "type": "team",
                    "team_id": team.id,
                    "assigned_by_admin": is_admin,
                    "assigned_by_team_lead": is_team_lead,
                    "assignee_kept": old_assignee.id if old_assignee else None
                }
            )

            return ticket

        # ======================
        # AGENT/SUPPORT ASSIGNMENT
        # ======================
        if assign_type == "agent":
            try:
                agent = User.objects.get(id=obj_id)
            except User.DoesNotExist:
                raise ValidationError("User not found")

            # Get agent's role
            role_name = TicketService._get_user_role(agent)

            # Allow admin to assign to anyone, but restrict others to allowed roles
            if not is_admin and role_name not in ALLOWED_ASSIGNEE_ROLES:
                allowed_roles_display = ", ".join(role.lower() for role in ALLOWED_ASSIGNEE_ROLES)
                raise ValidationError(f"Only {allowed_roles_display} can be assigned")

            # Additional validation for non-admins
            if not is_admin:
                # Check if agent is active
                if not agent.is_active:
                    raise ValidationError("Cannot assign to inactive user")
                
                # Team leads can only assign agents from their team
                if is_team_lead:
                    if agent.team_id != requesting_user.team_id:
                        raise ValidationError("You can only assign agents from your team")

            # ✅ KEEP existing team assignment - DO NOT clear team
            ticket.assigned_to = agent
            # DO NOT: ticket.team = None  ← Keep the team!
            ticket.assigned_by = requesting_user
            ticket.status = "ASSIGNED"
            ticket.save()

            # History (FULL TRACE)
            team_info = f" (with team {old_team})" if old_team else ""
            comment = f"Assigned to {role_name.lower()} {agent.get_full_name() or agent.username}{team_info}"
            if is_admin:
                comment += " (admin override)"
            
            TicketHistory.objects.create(
                ticket=ticket,
                action="ASSIGNED",
                comment=comment,
                old_team=old_team,
                new_team=old_team,  # Keep the same team
                old_assignee=old_assignee,
                new_assignee=agent,
                created_by=requesting_user,
                metadata={
                    "type": "agent",
                    "agent_id": agent.id,
                    "role": role_name,
                    "assigned_by_admin": is_admin,
                    "assigned_by_team_lead": is_team_lead,
                    "team_kept": old_team.id if old_team else None
                }
            )

            return ticket

        raise ValidationError("Invalid type. Use 'agent' or 'team'")

    # ---------- ADD COMMENT ----------
    @staticmethod
    def add_comment(ticket, request):
        comment = request.data.get("comment")
        if not comment:
            raise ValueError("Comment text is required")
        history = TicketHistory.objects.create(
            ticket=ticket,
            action="COMMENTED",
            comment=comment,
            created_by=request.user if request.user.is_authenticated else None,
        )
        return history