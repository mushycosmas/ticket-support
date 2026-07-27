import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework.exceptions import ValidationError, PermissionDenied

from ..models import Ticket, Customer, TicketHistory
from apps.users.models import Team
from apps.channels.models import Channel  

User = get_user_model()


# =========================
# PERMISSION SYSTEM - 100% Permission Based
# =========================
class TicketPermissions:
    """
    Complete permission-based access control for tickets.
    No hardcoded roles - everything is driven by permissions.
    """
    
    # ============================================================
    # PERMISSION CODENAMES
    # ============================================================
    
    # Ticket permissions
    VIEW_TICKET = 'view_ticket'
    ADD_TICKET = 'add_ticket'
    EDIT_TICKET = 'edit_ticket'
    DELETE_TICKET = 'delete_ticket'
    
    # Assignment permissions
    ASSIGN_TICKET = 'assign_ticket'
    ASSIGN_TICKET_TO_SUPPORT = 'assign_ticket_to_support'  # ✅ NEW
    ASSIGN_TICKET_TO_TEAM = 'assign_ticket_to_team'        # ✅ NEW
    ASSIGN_ANY_USER = 'assign_any_user'
    CAN_BE_ASSIGNED = 'can_be_assigned'
    
    # Workflow permissions
    START_PROGRESS = 'start_progress'
    RESOLVE_TICKET = 'resolve_ticket'
    CLOSE_TICKET = 'close_ticket'
    REOPEN_TICKET = 'reopen_ticket'
    
    # Team permissions
    CHANGE_TICKET_TEAM = 'change_ticket_team'
    MANAGE_TEAM_TICKETS = 'manage_team_tickets'
    VIEW_TEAM_TICKETS = 'view_team_tickets'
    
    # Leadership permission
    CAN_LEAD_TEAM = 'can_lead_team'
    
    # Comment permissions
    ADD_COMMENT = 'add_comment'
    EDIT_COMMENT = 'edit_comment'
    DELETE_COMMENT = 'delete_comment'
    
    # ============================================================
    # CORE PERMISSION CHECK
    # ============================================================
    
    @staticmethod
    def has_permission(user, permission_codename):
        """
        Check if user has a specific permission.
        Superuser always has all permissions.
        """
        if not user:
            return False
        
        # Superuser has all permissions
        if user.is_superuser:
            return True
        
        # Check if user has the permission via their role
        if hasattr(user, 'role') and user.role:
            return user.role.permissions.filter(codename=permission_codename).exists()
        
        return False
    
    # ============================================================
    # PERMISSION CHECKS
    # ============================================================
    
    @staticmethod
    def can_view_ticket(user, ticket=None):
        """Check if user can view a ticket."""
        if not user:
            return False
        
        if user.is_superuser:
            return True
        
        if TicketPermissions.has_permission(user, TicketPermissions.VIEW_TICKET):
            return True
        
        if ticket and ticket.team_id:
            if TicketPermissions.has_permission(user, TicketPermissions.VIEW_TEAM_TICKETS):
                return user.teams.filter(id=ticket.team_id).exists()
        
        return False
    
    @staticmethod
    def can_create_ticket(user):
        """Check if user can create a ticket."""
        if not user:
            return False
        
        if user.is_superuser:
            return True
        
        return TicketPermissions.has_permission(user, TicketPermissions.ADD_TICKET)
    
    @staticmethod
    def can_edit_ticket(user, ticket=None):
        """Check if user can edit a ticket."""
        if not user:
            return False
        
        if user.is_superuser:
            return True
        
        if TicketPermissions.has_permission(user, TicketPermissions.EDIT_TICKET):
            return True
        
        if ticket and ticket.team_id:
            if TicketPermissions.has_permission(user, TicketPermissions.MANAGE_TEAM_TICKETS):
                return user.teams.filter(id=ticket.team_id).exists()
        
        return False
    
    @staticmethod
    def can_delete_ticket(user, ticket=None):
        """Check if user can delete a ticket."""
        if not user:
            return False
        
        if user.is_superuser:
            return True
        
        return TicketPermissions.has_permission(user, TicketPermissions.DELETE_TICKET)
    
    # ============================================================
    # ✅ UPDATED: ASSIGN PERMISSIONS
    # ============================================================
    
    @staticmethod
    def can_assign_ticket(user, ticket=None):
        """
        Check if user can assign a ticket.
        Supports: assign_ticket, assign_ticket_to_support, assign_ticket_to_team
        """
        if not user:
            return False
        
        # Superuser can assign
        if user.is_superuser:
            return True
        
        # Check main assign_ticket permission
        if TicketPermissions.has_permission(user, TicketPermissions.ASSIGN_TICKET):
            return True
        
        # ✅ Check assign_ticket_to_support permission
        if TicketPermissions.has_permission(user, TicketPermissions.ASSIGN_TICKET_TO_SUPPORT):
            return True
        
        # ✅ Check assign_ticket_to_team permission
        if TicketPermissions.has_permission(user, TicketPermissions.ASSIGN_TICKET_TO_TEAM):
            return True
        
        # Allow if user has manage_team_tickets permission
        if ticket and ticket.team_id:
            if TicketPermissions.has_permission(user, TicketPermissions.MANAGE_TEAM_TICKETS):
                return user.teams.filter(id=ticket.team_id).exists()
        
        # Allow if user has edit_ticket permission
        if TicketPermissions.has_permission(user, TicketPermissions.EDIT_TICKET):
            return True
        
        return False
    
    @staticmethod
    def can_assign_to_user(assigner, assignee):
        """
        Check if assigner can assign to assignee.
        Uses permissions instead of hardcoded roles.
        """
        if not assigner or not assignee:
            return False
        
        # Superuser can assign to anyone
        if assigner.is_superuser:
            return True
        
        # Check if assigner has assign_any_user permission
        if TicketPermissions.has_permission(assigner, TicketPermissions.ASSIGN_ANY_USER):
            return True
        
        # ✅ Check if assigner has assign_ticket_to_support permission
        if TicketPermissions.has_permission(assigner, TicketPermissions.ASSIGN_TICKET_TO_SUPPORT):
            # Check if assignee has can_be_assigned permission
            if TicketPermissions.has_permission(assignee, TicketPermissions.CAN_BE_ASSIGNED):
                return True
            # Check if assignee has SUPPORT role (backward compatibility)
            if hasattr(assignee, 'role') and assignee.role:
                if hasattr(assignee.role, 'name') and assignee.role.name.upper() == 'SUPPORT':
                    return True
        
        # ✅ Check if assigner has assign_ticket_to_team permission
        if TicketPermissions.has_permission(assigner, TicketPermissions.ASSIGN_TICKET_TO_TEAM):
            # Check if assignee is in the same team
            if assigner.teams.filter(id__in=assignee.teams.all()).exists():
                return True
        
        # Check if assignee has can_be_assigned permission
        if TicketPermissions.has_permission(assignee, TicketPermissions.CAN_BE_ASSIGNED):
            return True
        
        return False
    
    @staticmethod
    def can_start_progress(user, ticket=None):
        """Check if user can start progress on a ticket."""
        if not user:
            return False
        
        if user.is_superuser:
            return True
        
        if TicketPermissions.has_permission(user, TicketPermissions.START_PROGRESS):
            return True
        
        if ticket and ticket.team_id:
            if TicketPermissions.has_permission(user, TicketPermissions.MANAGE_TEAM_TICKETS):
                return user.teams.filter(id=ticket.team_id).exists()
        
        return False
    
    @staticmethod
    def can_resolve_ticket(user, ticket=None):
        """Check if user can resolve a ticket."""
        if not user:
            return False
        
        if user.is_superuser:
            return True
        
        if TicketPermissions.has_permission(user, TicketPermissions.RESOLVE_TICKET):
            return True
        
        if ticket and ticket.team_id:
            if TicketPermissions.has_permission(user, TicketPermissions.MANAGE_TEAM_TICKETS):
                return user.teams.filter(id=ticket.team_id).exists()
        
        return False
    
    @staticmethod
    def can_close_ticket(user, ticket=None):
        """Check if user can close a ticket."""
        if not user:
            return False
        
        if user.is_superuser:
            return True
        
        if TicketPermissions.has_permission(user, TicketPermissions.CLOSE_TICKET):
            return True
        
        if ticket and ticket.team_id:
            if TicketPermissions.has_permission(user, TicketPermissions.MANAGE_TEAM_TICKETS):
                return user.teams.filter(id=ticket.team_id).exists()
        
        return False
    
    @staticmethod
    def can_reopen_ticket(user, ticket=None):
        """Check if user can reopen a ticket."""
        if not user:
            return False
        
        if user.is_superuser:
            return True
        
        if TicketPermissions.has_permission(user, TicketPermissions.REOPEN_TICKET):
            return True
        
        if ticket and ticket.team_id:
            if TicketPermissions.has_permission(user, TicketPermissions.MANAGE_TEAM_TICKETS):
                return user.teams.filter(id=ticket.team_id).exists()
        
        return False
    
    @staticmethod
    def can_change_team(user, ticket=None):
        """Check if user can change a ticket's team."""
        if not user:
            return False
        
        if user.is_superuser:
            return True
        
        return TicketPermissions.has_permission(user, TicketPermissions.CHANGE_TICKET_TEAM)
    
    @staticmethod
    def can_comment(user, ticket=None):
        """Check if user can comment on a ticket."""
        if not user:
            return False
        
        if user.is_superuser:
            return True
        
        if TicketPermissions.has_permission(user, TicketPermissions.ADD_COMMENT):
            return True
        
        if ticket and ticket.team_id:
            if TicketPermissions.has_permission(user, TicketPermissions.MANAGE_TEAM_TICKETS):
                return user.teams.filter(id=ticket.team_id).exists()
        
        return False


# =========================
# WORKFLOW LAYER (state machine)
# =========================
class TicketWorkflow:
    """Valid transitions for ticket status."""

    @staticmethod
    def assign(ticket, user):
        ticket.status = "ASSIGNED"
        ticket.assigned_to = user
        ticket.save()
        return ticket

    @staticmethod
    def start_progress(ticket, user=None):
        """
        Start progress on a ticket.
        """
        if ticket.status not in ("ASSIGNED", "OPEN"):
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
    """
    Handles all ticket operations with 100% permission-based access control.
    No hardcoded roles - everything is driven by permissions.
    """

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
    def _get_team_lead(team):
        """
        Get the team lead for a given team.
        Based purely on the 'can_lead_team' permission.
        """
        if not team:
            return None
        
        # Find users who are members of this team AND have the 'can_lead_team' permission
        team_lead = User.objects.filter(
            teams=team,
            role__permissions__codename='can_lead_team'
        ).first()
        
        return team_lead

    @staticmethod
    def _get_team_from_channel(channel_id):
        """
        Get the team from a channel.
        Returns (team_id, team_lead) tuple.
        """
        team_id = None
        team_lead = None
        
        if channel_id:
            try:
                channel = Channel.objects.select_related('team').get(id=channel_id)
                if channel.team_id:
                    team_id = channel.team_id
                    team_lead = TicketService._get_team_lead(channel.team)
            except Channel.DoesNotExist:
                pass
        
        return team_id, team_lead

    @staticmethod
    def _get_or_create_customer(data, request_user_id):
        """
        Get or create a customer from the request data.
        Handles duplicate NIDA numbers gracefully.
        """
        email = data.get("customer_email")
        phone = data.get("customer_phone")
        name = data.get("customer_name")
        nida_number = data.get("customer_nida")
        gender = data.get("customer_gender")
        
        customer = None
        created = False
        
        # If no identifying info, return None
        if not any([email, phone, nida_number]):
            return None, False
        
        try:
            # Try to get or create customer
            customer, created = Customer.get_or_create_customer(
                email=email,
                phone=phone,
                full_name=name,
                nida_number=nida_number,
                gender=gender,
                created_by_id=request_user_id,
            )
            return customer, created
            
        except IntegrityError as e:
            # Handle duplicate NIDA number error
            if "Duplicate entry" in str(e) and "nida_number" in str(e):
                # Find existing customer with this NIDA
                if nida_number:
                    customer = Customer.objects.filter(nida_number=nida_number).first()
                    if customer:
                        # Update existing customer with new info
                        if email and not customer.email:
                            customer.email = email
                        if phone and not customer.phone:
                            customer.phone = phone
                        if name and name != 'Unknown' and not customer.full_name:
                            customer.full_name = name
                        if gender and not customer.gender:
                            customer.gender = gender
                        customer.save(update_fields=['email', 'phone', 'full_name', 'gender'])
                        return customer, False
                
                # If we couldn't find by NIDA, try by email or phone
                if email:
                    customer = Customer.objects.filter(email=email).first()
                    if customer:
                        return customer, False
                if phone:
                    customer = Customer.objects.filter(phone=phone).first()
                    if customer:
                        return customer, False
            
            # Re-raise other integrity errors
            raise e
        
        except Exception as e:
            print(f"❌ Customer error: {e}")
            # Try to find existing customer by email or phone
            if email:
                customer = Customer.objects.filter(email=email).first()
                if customer:
                    return customer, False
            if phone:
                customer = Customer.objects.filter(phone=phone).first()
                if customer:
                    return customer, False
            raise e

    # ---------- CREATE ----------
    @staticmethod
    @transaction.atomic
    def create_ticket(request):
        """Create a new ticket with automatic team and team lead assignment."""
        data = request.data
        request_user = request.user if request.user.is_authenticated else None
        request_user_id = request_user.id if request_user else None

        # 🔒 Permission check: can create ticket
        if not TicketPermissions.can_create_ticket(request_user):
            raise PermissionDenied("You don't have permission to create tickets")

        # ----- Customer handling with duplicate protection -----
        customer, customer_created = TicketService._get_or_create_customer(data, request_user_id)

        # ----- Foreign keys -----
        category_id = TicketService.safe_int(data.get("category_id") or data.get("category"))
        channel_id = TicketService.safe_int(data.get("channel_id") or data.get("channel"))
        street_id = TicketService.safe_int(data.get("street_id"))
        team_id = TicketService.safe_int(data.get("team"))
        assigned_to_id = TicketService.safe_int(data.get("assigned_to"))
        assigned_by_id = TicketService.safe_int(data.get("assigned_by"))
        template_id = TicketService.safe_int(data.get("template"))

        # ----- FLOW: Channel → Team → Team Lead -----
        final_team_id = team_id
        team_lead = None
        
        if channel_id:
            channel_team_id, channel_team_lead = TicketService._get_team_from_channel(channel_id)
            if channel_team_id:
                final_team_id = channel_team_id
                team_lead = channel_team_lead
        
        if not team_lead and final_team_id:
            try:
                team = Team.objects.get(id=final_team_id)
                team_lead = TicketService._get_team_lead(team)
            except Team.DoesNotExist:
                pass

        # ✅ Determine initial status
        initial_status = "OPEN"
        
        # If assigned_to is provided and assignable, set to IN_PROGRESS
        if assigned_to_id:
            assigned_user = User.objects.filter(id=assigned_to_id).first()
            if assigned_user and TicketPermissions.can_assign_to_user(request_user, assigned_user):
                initial_status = "IN_PROGRESS"
        elif team_lead:
            initial_status = "IN_PROGRESS"

        # ----- Create ticket -----
        ticket = Ticket.objects.create(
            ticket_number=f"TKT-{uuid.uuid4().hex[:8].upper()}",
            title=data.get("title"),
            description=data.get("description", ""),
            priority=data.get("priority", "MEDIUM"),
            status=initial_status,
            category_id=category_id,
            channel_id=channel_id,
            street_id=street_id,
            customer=customer,
            template_id=template_id,
            team_id=final_team_id,
            assigned_to=team_lead if team_lead else None,
        )

        # ----- Override assigned_to if explicitly provided -----
        if assigned_to_id:
            user = User.objects.filter(id=assigned_to_id).first()
            if user and TicketPermissions.can_assign_to_user(request_user, user):
                ticket.assigned_to = user
                ticket.status = "IN_PROGRESS"
        
        # ----- Set assigned_by -----
        if assigned_by_id:
            by_user = User.objects.filter(id=assigned_by_id).first()
            if by_user:
                ticket.assigned_by = by_user
        elif request_user:
            ticket.assigned_by = request_user

        ticket.save()

        # ----- Create history entry -----
        TicketHistory.objects.create(
            ticket=ticket,
            action="CREATED",
            comment=f"Ticket created with status: {ticket.status}",
            created_by=request_user,
            metadata={
                "title": ticket.title,
                "description": ticket.description[:100] if ticket.description else "",
                "street_id": street_id,
                "channel_id": channel_id,
                "team_id": final_team_id,
                "team_lead_id": team_lead.id if team_lead else None,
                "assigned_to": assigned_to_id,
                "assigned_by": assigned_by_id,
                "template_id": template_id,
                "customer_id": customer.id if customer else None,
                "customer_created": customer_created,
                "initial_status": initial_status,
                "auto_assigned_from_channel": bool(channel_id and final_team_id),
            }
        )

        return ticket

    # ---------- UNIFIED ASSIGN ----------
    @staticmethod
    def assign(ticket, request):
        """
        Unified assign method that handles both agent/support and team assignment.
        """
        user = request.user if request.user.is_authenticated else None
        
        # 🔒 Permission check: can assign ticket
        if not TicketPermissions.can_assign_ticket(user, ticket):
            raise PermissionDenied("You don't have permission to assign tickets")
        
        assign_type = request.data.get("type")
        obj_id = request.data.get("id")

        if not assign_type or not obj_id:
            raise ValidationError("type and id are required")

        if assign_type == "agent":
            return TicketService.assign_worker(ticket, request)
        elif assign_type == "team":
            return TicketService.change_team(ticket, request)
        else:
            raise ValidationError("Invalid type. Use 'agent' or 'team'")

    # ---------- ASSIGN WORKER ----------
    @staticmethod
    def assign_worker(ticket, request):
        """
        Assign a user to the ticket manually.
        Uses permissions to determine if the user can be assigned.
        """
        user = request.user if request.user.is_authenticated else None
        worker_id = request.data.get("id") or request.data.get("agent_id")
        
        if not worker_id:
            raise ValidationError("worker_id is required")

        try:
            worker = User.objects.get(id=worker_id)
        except User.DoesNotExist:
            raise ValidationError("User not found")

        # 🔒 Check if user can be assigned to
        if not TicketPermissions.can_assign_to_user(user, worker):
            raise ValidationError("This user cannot be assigned to tickets")
        
        # 🔒 Additional validation: check if worker is in the same team
        if not TicketPermissions.has_permission(user, TicketPermissions.ASSIGN_ANY_USER):
            if not worker.is_active:
                raise ValidationError("Cannot assign to inactive user")
            
            # Check if worker is in the same team
            if ticket.team_id:
                user_team_ids = user.teams.values_list('id', flat=True)
                worker_team_ids = worker.teams.values_list('id', flat=True)
                
                if not set(user_team_ids).intersection(set(worker_team_ids)):
                    raise ValidationError("Worker must be in the same team")

        old_assignee = ticket.assigned_to
        old_team = ticket.team
        old_status = ticket.status

        # Assign the worker
        ticket.assigned_to = worker
        ticket.assigned_by = user
        ticket.status = "IN_PROGRESS"
        ticket.save()

        # Create history entry
        comment = f"Assigned to {worker.get_full_name() or worker.username}"
        
        if TicketPermissions.has_permission(user, TicketPermissions.ASSIGN_ANY_USER):
            comment += " (admin override)"
        
        if old_status != ticket.status:
            comment += f" (status changed from {old_status} to {ticket.status})"
        
        TicketHistory.objects.create(
            ticket=ticket,
            action="ASSIGNED",
            comment=comment,
            old_assignee=old_assignee,
            new_assignee=worker,
            old_team=old_team,
            new_team=old_team,
            old_status=old_status,
            new_status=ticket.status,
            created_by=user,
            metadata={
                "worker_id": worker.id,
                "assigned_by": user.id if user else None,
                "assigned_by_permission": TicketPermissions.has_permission(user, TicketPermissions.ASSIGN_ANY_USER),
                "team_id": ticket.team_id,
                "status_changed": old_status != ticket.status,
            }
        )

        return ticket

    # ---------- CHANGE TEAM ----------
    @staticmethod
    def change_team(ticket, request):
        """
        Change the team for a ticket.
        Requires change_ticket_team permission.
        """
        user = request.user if request.user.is_authenticated else None
        team_id = request.data.get("id") or request.data.get("team_id")
        
        if not team_id:
            raise ValidationError("team_id is required")

        # 🔒 Permission check: can change team
        if not TicketPermissions.can_change_team(user, ticket):
            raise PermissionDenied("You don't have permission to change ticket team")

        try:
            new_team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise ValidationError("Team not found")

        old_team = ticket.team
        old_assignee = ticket.assigned_to
        old_status = ticket.status

        ticket.team = new_team
        ticket.assigned_by = user
        ticket.save()

        # Get new team lead
        new_team_lead = TicketService._get_team_lead(new_team)
        
        if new_team_lead:
            ticket.assigned_to = new_team_lead
            ticket.status = "IN_PROGRESS"
            ticket.save()
            new_assignee = new_team_lead
        else:
            new_assignee = old_assignee

        TicketHistory.objects.create(
            ticket=ticket,
            action="TEAM_CHANGED",
            comment=f"Team changed from {old_team.name if old_team else 'None'} to {new_team.name}",
            old_team=old_team,
            new_team=new_team,
            old_assignee=old_assignee,
            new_assignee=new_assignee,
            old_status=old_status,
            new_status=ticket.status,
            created_by=user,
            metadata={
                "old_team_id": old_team.id if old_team else None,
                "new_team_id": new_team.id,
                "team_lead_auto_assigned": bool(new_team_lead),
                "status_changed": old_status != ticket.status,
            }
        )

        return ticket

    # ---------- START PROGRESS ----------
    @staticmethod
    def start_progress(ticket, request):
        """
        Start progress on a ticket.
        """
        user = request.user if request.user.is_authenticated else None
        
        if not user:
            raise PermissionDenied("Authentication required")
        
        # 🔒 Permission check: can start progress
        if not TicketPermissions.can_start_progress(user, ticket):
            raise PermissionDenied(
                "You don't have permission to start progress on this ticket."
            )
        
        old_status = ticket.status
        
        try:
            ticket = TicketWorkflow.start_progress(ticket, user)
        except ValueError as e:
            raise ValueError(str(e))
        
        TicketHistory.objects.create(
            ticket=ticket,
            action="STARTED_PROGRESS",
            comment=f"Started progress by {user.get_full_name() or user.username}",
            old_status=old_status,
            new_status=ticket.status,
            created_by=user,
            metadata={
                "user_id": user.id,
                "assigned_to": ticket.assigned_to.id if ticket.assigned_to else None,
            }
        )
        
        return ticket

    # ---------- RESOLVE ----------
    @staticmethod
    def resolve(ticket, request, comment=""):
        """Resolve a ticket."""
        user = request.user if request.user.is_authenticated else None
        
        # 🔒 Permission check: can resolve ticket
        if not TicketPermissions.can_resolve_ticket(user, ticket):
            raise PermissionDenied(
                "You don't have permission to resolve this ticket."
            )
        
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
            created_by=user,
            metadata={"comment": comment}
        )
        return ticket

    # ---------- CLOSE ----------
    @staticmethod
    def close(ticket, request, comment=""):
        """Close a ticket."""
        user = request.user if request.user.is_authenticated else None
        
        # 🔒 Permission check: can close ticket
        if not TicketPermissions.can_close_ticket(user, ticket):
            raise PermissionDenied(
                "You don't have permission to close this ticket."
            )
        
        old_status = ticket.status
        ticket = TicketWorkflow.close(ticket)
        
        TicketHistory.objects.create(
            ticket=ticket,
            action="CLOSED",
            comment=comment,
            old_status=old_status,
            new_status=ticket.status,
            created_by=user,
            metadata={"comment": comment}
        )
        return ticket

    # ---------- REOPEN ----------
    @staticmethod
    def reopen(ticket, request, comment=""):
        """Reopen a closed or resolved ticket."""
        user = request.user if request.user.is_authenticated else None
        
        # 🔒 Permission check: can reopen ticket
        if not TicketPermissions.can_reopen_ticket(user, ticket):
            raise PermissionDenied(
                "You don't have permission to reopen this ticket."
            )
        
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
            created_by=user,
            metadata={"comment": comment}
        )
        return ticket

    # ---------- ADD COMMENT ----------
    @staticmethod
    def add_comment(ticket, request):
        """Add a comment to a ticket."""
        user = request.user if request.user.is_authenticated else None
        comment = request.data.get("comment")
        
        if not comment:
            raise ValueError("Comment text is required")
        
        # 🔒 Permission check: can comment
        if not TicketPermissions.can_comment(user, ticket):
            raise PermissionDenied("You don't have permission to comment on this ticket")
        
        history = TicketHistory.objects.create(
            ticket=ticket,
            action="COMMENTED",
            comment=comment,
            created_by=user,
        )
        return history

    # ---------- GET TICKET OWNER ----------
    @staticmethod
    def get_ticket_owner(ticket):
        """Get the current owner of the ticket."""
        if ticket.assigned_to:
            return ticket.assigned_to
        if ticket.team:
            return TicketService._get_team_lead(ticket.team)
        return None

    # ---------- GET TICKET SUMMARY ----------
    @staticmethod
    def get_ticket_summary(ticket):
        """Get a summary of the ticket with all related information."""
        return {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "title": ticket.title,
            "status": ticket.status,
            "priority": ticket.priority,
            "created_at": ticket.created_at,
            "assigned_to": ticket.assigned_to.get_full_name() if ticket.assigned_to else None,
            "team": ticket.team.name if ticket.team else None,
            "channel": ticket.channel.name if ticket.channel else None,
            "customer": ticket.customer.full_name if ticket.customer else None,
            "owner": TicketService.get_ticket_owner(ticket).get_full_name() if TicketService.get_ticket_owner(ticket) else None,
        }