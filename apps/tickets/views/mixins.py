# apps/tickets/views/mixins.py
from rest_framework.decorators import action
from rest_framework.response import Response

from ..services.ticket_service import TicketService


class TicketResolveMixin:
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        comment = request.data.get('comment', '')
        try:
            ticket = TicketService.resolve(ticket, request, comment=comment)
            serializer = self.get_serializer(ticket)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)


class TicketCloseMixin:
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        ticket = self.get_object()
        comment = request.data.get('comment', '')
        try:
            ticket = TicketService.close(ticket, request, comment=comment)
            serializer = self.get_serializer(ticket)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)


class TicketReopenMixin:
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        ticket = self.get_object()
        comment = request.data.get('comment', '')
        try:
            ticket = TicketService.reopen(ticket, request, comment=comment)
            serializer = self.get_serializer(ticket)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)


class TicketAssignMixin:
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        try:
            ticket = TicketService.assign(ticket, request)
            serializer = self.get_serializer(ticket)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)


class TicketCommentMixin:
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        ticket = self.get_object()
        try:
            history = TicketService.add_comment(ticket, request)
            return Response({
                'status': 'Comment added',
                'history_id': history.id,
                'comment': history.comment,
                'created_at': history.created_at.isoformat()
            })
        except ValueError as e:
            return Response({"error": str(e)}, status=400)


class TicketOverdueMixin:
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        from django.utils import timezone
        from datetime import timedelta
        threshold = timezone.now() - timedelta(days=2)
        tickets = self.get_queryset().filter(
            created_at__lt=threshold
        ).exclude(status__in=['RESOLVED', 'CLOSED'])
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)


class TicketAgingMixin:
    @action(detail=False, methods=['get'])
    def aging(self, request):
        from django.utils import timezone
        tickets = self.get_queryset().exclude(status__in=['RESOLVED', 'CLOSED'])
        result = []
        for ticket in tickets:
            days_old = (timezone.now() - ticket.created_at).days
            result.append({
                'id': ticket.id,
                'ticket_number': ticket.ticket_number,
                'title': ticket.title,
                'status': ticket.status,
                'priority': ticket.priority,
                'created_at': ticket.created_at.isoformat(),
                'days_old': days_old,
                'assigned_to_name': ticket.assigned_to.get_full_name() or ticket.assigned_to.username if ticket.assigned_to else None,
                'customer_name': ticket.customer.full_name if ticket.customer else None,
            })
        result.sort(key=lambda x: x['days_old'], reverse=True)
        return Response(result)