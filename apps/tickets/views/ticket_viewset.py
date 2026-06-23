from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Ticket
from ..serializers import TicketSerializer
from ..services.ticket_service import TicketService
from ..queries.ticket_query import TicketQuery
from ..builders.ticket_timeline import TicketTimelineBuilder

from .mixins import (
    TicketResolveMixin,
    TicketCloseMixin,
    TicketReopenMixin,
    TicketAssignMixin,
    TicketCommentMixin,
    TicketOverdueMixin,
    TicketAgingMixin,
)


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
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "track"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return TicketQuery(self.request).get_queryset()

    def list(self, request, *args, **kwargs):
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
        ticket = TicketService.create_ticket(request)
        serializer = self.get_serializer(ticket)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        ticket = self.get_object()
        data = self.get_serializer(ticket).data
        data["timeline"] = TicketTimelineBuilder.build(ticket)
        data["lastUpdate"] = ticket.updated_at.isoformat()
        return Response(data)

    # ---------- SOFT DELETE OVERRIDE ----------
    def destroy(self, request, *args, **kwargs):
        """Soft delete a ticket."""
        ticket = self.get_object()
        ticket.soft_delete()
        return Response(
            {"message": "Ticket soft-deleted successfully", "id": ticket.id},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore a soft-deleted ticket."""
        # Use all_objects to include soft-deleted records
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
        # Get user role name safely
        role_name = None
        if hasattr(request.user, 'role') and request.user.role:
            role_name = request.user.role.name.upper() if hasattr(request.user.role, 'name') else str(request.user.role).upper()
        elif hasattr(request.user, 'role_name') and request.user.role_name:
            role_name = request.user.role_name.upper()

        # Allow access if role is ADMIN or user is staff (backup)
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