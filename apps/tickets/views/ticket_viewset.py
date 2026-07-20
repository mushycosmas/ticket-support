from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.utils import timezone
import logging

from ..models import Ticket, TicketHistory
from apps.categories.models import Category
from ..serializers import TicketSerializer
from ..services.ticket_service import TicketService
from ..queries.ticket_query import TicketQuery
from ..builders.ticket_timeline import TicketTimelineBuilder

# Import SMS service
from apps.notifications.services.ticket_sms_service import TicketSMSService

from .mixins import (
    TicketResolveMixin,
    TicketCloseMixin,
    TicketReopenMixin,
    TicketAssignMixin,
    TicketCommentMixin,
    TicketOverdueMixin,
    TicketAgingMixin,
)

logger = logging.getLogger(__name__)


class TicketViewSet(
    TicketResolveMixin,
    TicketCloseMixin,
    TicketReopenMixin,
    TicketAssignMixin,
    TicketCommentMixin,
    TicketOverdueMixin,
    TicketAgingMixin,
    viewsets.ModelViewSet,
):
    """
    Ticket ViewSet with full CRUD operations and custom actions.
    Supports: Create, Read, Update, Delete (soft), Assign, Resolve, Close, Reopen, Comment, 
    Update Priority, Update Category, Update Status, and more.
    """
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Allow unauthenticated access for create and track actions."""
        if self.action in ["create", "track"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Get queryset with role-based filtering."""
        return TicketQuery(self.request).get_queryset()

    # ==========================================
    # STANDARD CRUD OPERATIONS
    # ==========================================

    def list(self, request, *args, **kwargs):
        """List tickets with pagination and filters."""
        queryset = self.get_queryset()
        queryset = TicketQuery(request).apply_filters(queryset)

        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 15))
        start = (page - 1) * page_size
        end = start + page_size

        serializer = self.get_serializer(queryset[start:end], many=True)
        return Response({
            "count": queryset.count(),
            "page": page,
            "page_size": page_size,
            "results": serializer.data
        })

    def create(self, request, *args, **kwargs):
        """Create a new ticket and send SMS notification."""
        ticket = TicketService.create_ticket(request)
        
        # ============================================================
        # 📱 SEND SMS WHEN TICKET IS CREATED
        # ============================================================
        if ticket.customer and ticket.customer.phone:
            try:
                sms_sent = TicketSMSService.send_ticket_created_sms(ticket)
                if sms_sent:
                    logger.info(f"✅ SMS sent for ticket {ticket.ticket_number} to {ticket.customer.phone}")
                else:
                    logger.warning(f"⚠️ SMS failed for ticket {ticket.ticket_number}")
            except Exception as e:
                logger.error(f"❌ Error sending SMS for ticket {ticket.ticket_number}: {str(e)}")
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single ticket with timeline and last update."""
        ticket = self.get_object()
        data = self.get_serializer(ticket).data
        data["timeline"] = TicketTimelineBuilder.build(ticket)
        data["lastUpdate"] = ticket.updated_at.isoformat()
        return Response(data)

    def update(self, request, *args, **kwargs):
        """Update a ticket fully."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Store old status for SMS check
        old_status = instance.status
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # ============================================================
        # 📱 SEND SMS WHEN TICKET IS CLOSED
        # ============================================================
        if (old_status != instance.status and 
            instance.status == 'CLOSED' and 
            instance.customer and 
            instance.customer.phone):
            try:
                sms_sent = TicketSMSService.send_ticket_closed_sms(instance)
                if sms_sent:
                    logger.info(f"✅ SMS sent for closed ticket {instance.ticket_number} to {instance.customer.phone}")
                else:
                    logger.warning(f"⚠️ SMS failed for closed ticket {instance.ticket_number}")
            except Exception as e:
                logger.error(f"❌ Error sending SMS for closed ticket {instance.ticket_number}: {str(e)}")
        
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Soft delete a ticket."""
        ticket = self.get_object()
        ticket.soft_delete()
        return Response(
            {"message": "Ticket soft-deleted successfully", "id": ticket.id},
            status=status.HTTP_200_OK
        )

    # ==========================================
    # SOFT DELETE MANAGEMENT
    # ==========================================

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore a soft-deleted ticket."""
        ticket = Ticket.all_objects.get(pk=pk)
        if not ticket.is_deleted:
            return Response(
                {"error": "Ticket is not deleted"},
                status=status.HTTP_400_BAD_REQUEST
            )
        ticket.restore()
        return Response(
            {"message": "Ticket restored successfully", "id": ticket.id},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """List all soft-deleted tickets (admin only)."""
        role_name = self._get_user_role(request.user)

        if role_name != "ADMIN" and not request.user.is_staff:
            return Response(
                {"error": "Permission denied. Only administrators can view deleted tickets."},
                status=status.HTTP_403_FORBIDDEN
            )

        deleted_tickets = Ticket.all_objects.filter(deleted_at__isnull=False)
        page = self.paginate_queryset(deleted_tickets)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(deleted_tickets, many=True)
        return Response(serializer.data)

    # ==========================================
    # TICKET UPDATE ACTIONS
    # ==========================================

    @action(detail=True, methods=['patch'])
    def update_category(self, request, pk=None):
        """
        Update ticket category.
        Expected payload: { "category_id": 123 }
        """
        ticket = self.get_object()
        category_id = request.data.get('category_id')
        
        if category_id is None:
            raise ValidationError({"category_id": "This field is required."})
        
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise ValidationError({"category_id": f"Category with id {category_id} does not exist."})
        
        old_category = ticket.category
        old_category_name = old_category.name if old_category else "None"
        
        ticket.category = category
        ticket.save(update_fields=['category', 'updated_at'])
        
        TicketHistory.objects.create(
            ticket=ticket,
            action="CATEGORY_UPDATED",
            comment=f"Category updated from '{old_category_name}' to '{category.name}'",
            created_by=request.user,
            metadata={
                "old_category_id": old_category.id if old_category else None,
                "old_category_name": old_category_name,
                "new_category_id": category.id,
                "new_category_name": category.name
            }
        )
        
        return Response({
            "message": "Category updated successfully",
            "category_id": category.id,
            "category_name": category.name,
            "old_category": old_category_name
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def update_priority(self, request, pk=None):
        """
        Update ticket priority.
        Expected payload: { "priority": "HIGH" }
        Valid priorities: LOW, MEDIUM, HIGH, CRITICAL
        """
        ticket = self.get_object()
        priority = request.data.get('priority')
        
        if not priority:
            raise ValidationError({"priority": "This field is required."})
        
        valid_priorities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        if priority.upper() not in valid_priorities:
            raise ValidationError({
                "priority": f"Priority must be one of: {', '.join(valid_priorities)}"
            })
        
        old_priority = ticket.priority
        ticket.priority = priority.upper()
        ticket.save(update_fields=['priority', 'updated_at'])
        
        TicketHistory.objects.create(
            ticket=ticket,
            action="PRIORITY_UPDATED",
            comment=f"Priority updated from '{old_priority}' to '{ticket.priority}'",
            created_by=request.user,
            metadata={
                "old_priority": old_priority,
                "new_priority": ticket.priority
            }
        )
        
        return Response({
            "message": "Priority updated successfully",
            "priority": ticket.priority,
            "old_priority": old_priority
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update ticket status.
        Expected payload: { "status": "IN_PROGRESS" }
        Valid statuses: OPEN, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED
        """
        ticket = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value:
            raise ValidationError({"status": "This field is required."})
        
        valid_statuses = ['OPEN', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']
        if status_value.upper() not in valid_statuses:
            raise ValidationError({
                "status": f"Status must be one of: {', '.join(valid_statuses)}"
            })
        
        old_status = ticket.status
        ticket.status = status_value.upper()
        
        if ticket.status == 'RESOLVED' and not ticket.resolved_at:
            ticket.resolved_at = timezone.now()
        elif ticket.status != 'RESOLVED':
            ticket.resolved_at = None
            
        ticket.save(update_fields=['status', 'resolved_at', 'updated_at'])
        
        TicketHistory.objects.create(
            ticket=ticket,
            action="STATUS_UPDATED",
            comment=f"Status updated from '{old_status}' to '{ticket.status}'",
            created_by=request.user,
            metadata={
                "old_status": old_status,
                "new_status": ticket.status
            }
        )

        # ============================================================
        # 📱 SEND SMS WHEN TICKET IS CLOSED VIA STATUS UPDATE
        # ============================================================
        if (old_status != ticket.status and 
            ticket.status == 'CLOSED' and 
            ticket.customer and 
            ticket.customer.phone):
            try:
                sms_sent = TicketSMSService.send_ticket_closed_sms(ticket)
                if sms_sent:
                    logger.info(f"✅ SMS sent for closed ticket {ticket.ticket_number} to {ticket.customer.phone}")
                else:
                    logger.warning(f"⚠️ SMS failed for closed ticket {ticket.ticket_number}")
            except Exception as e:
                logger.error(f"❌ Error sending SMS for closed ticket {ticket.ticket_number}: {str(e)}")
        
        return Response({
            "message": "Status updated successfully",
            "status": ticket.status,
            "old_status": old_status
        }, status=status.HTTP_200_OK)

    # ==========================================
    # HELPER METHODS
    # ==========================================

    def _get_user_role(self, user):
        """
        Extract user role from various possible field structures.
        Handles both string and object role fields.
        """
        if not user:
            return None
        
        if hasattr(user, "role") and user.role:
            if hasattr(user.role, "name"):
                return user.role.name.upper()
            elif isinstance(user.role, str):
                return user.role.upper()
        
        if hasattr(user, "role_name") and user.role_name:
            return user.role_name.upper()
        
        return None