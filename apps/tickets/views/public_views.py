from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.db.models import Q

from ..models import Ticket, Customer
from ..serializers import TicketSerializer


# =========================
# TEST ENDPOINT
# =========================
@api_view(['GET'])
@permission_classes([AllowAny])
def test_endpoint(request):
    """Test endpoint to verify tickets app is working"""
    return Response({
        'message': 'Tickets API is working!',
        'status': 'ok',
        'endpoints': {
            'list_tickets': 'GET /api/tickets/tickets/',
            'create_ticket': 'POST /api/tickets/tickets/',
            'get_ticket': 'GET /api/tickets/tickets/{id}/',
            'resolve_ticket': 'POST /api/tickets/tickets/{id}/resolve/',
            'close_ticket': 'POST /api/tickets/tickets/{id}/close/',
            'list_customers': 'GET /api/tickets/customers/',
            'track_ticket': 'GET /api/tickets/tickets/track/?query=XXX'
        }
    })


# =========================
# TRACK TICKET (SMART SEARCH)
# =========================
@api_view(['GET'])
@permission_classes([AllowAny])
def track_ticket(request):
    """
    Public endpoint to track ticket by:
    - ticket_number
    - customer phone
    - customer nida
    """

    query = (
        request.query_params.get('query')
        or request.query_params.get('ticket_number')
        or request.query_params.get('phone')
        or request.query_params.get('nida')
    )

    if not query:
        return Response(
            {
                'error': 'query is required (ticket_number, phone, or nida)'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # =========================
        # STEP 1: FIND BY TICKET NUMBER
        # =========================
        ticket = Ticket.objects.filter(
            ticket_number=query
        ).select_related('customer').first()

        # =========================
        # STEP 2: FIND BY CUSTOMER PHONE OR NIDA
        # =========================
        if not ticket:
            ticket = Ticket.objects.filter(
                Q(customer__phone=query) |
                Q(customer__nida_number=query)
            ).select_related('customer').first()

        # =========================
        # NOT FOUND
        # =========================
        if not ticket:
            return Response(
                {'error': f'No ticket found for "{query}"'},
                status=status.HTTP_404_NOT_FOUND
            )

        # =========================
        # SERIALIZE TICKET
        # =========================
        serializer = TicketSerializer(ticket)
        data = serializer.data

        # =========================
        # BUILD TIMELINE
        # =========================
        timeline = []

        for history in ticket.histories.all().order_by('created_at'):
            created_by = history.created_by

            timeline.append({
                'id': history.id,
                'date': history.created_at.isoformat(),
                'action': history.action,
                'message': history.display_message,
                'type': history.display_type,
                'comment': history.comment,

                # SAFE USER DATA
                'user': (
                    created_by.get_full_name()
                    if created_by else 'System'
                ),

                'user_role': (
                    created_by.role.name
                    if created_by and created_by.role
                    else None
                ),

                'is_comment': history.action == 'COMMENTED',
                'old_status': history.old_status,
                'new_status': history.new_status,
                'old_priority': history.old_priority,
                'new_priority': history.new_priority,
                'old_assignee': history.old_assignee,
                'new_assignee': history.new_assignee,
            })

        data['timeline'] = timeline
        data['lastUpdate'] = ticket.updated_at.isoformat()

        return Response(data)

    except Exception as e:
        print(f"Error in track_ticket: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =========================
# PUBLIC STATUS (OPTIONAL)
# =========================
@api_view(['GET'])
@permission_classes([AllowAny])
def public_ticket_status(request, ticket_number):
    """Direct ticket lookup via URL param"""

    try:
        ticket = Ticket.objects.filter(
            ticket_number=ticket_number
        ).select_related('customer').first()

        if not ticket:
            return Response(
                {'error': f'Ticket "{ticket_number}" not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TicketSerializer(ticket)
        data = serializer.data

        timeline = []

        for history in ticket.histories.all().order_by('created_at')[:10]:
            created_by = history.created_by

            timeline.append({
                'id': history.id,
                'date': history.created_at.isoformat(),
                'action': history.action,
                'message': history.display_message,
                'type': history.display_type,
                'comment': history.comment,
                'user': created_by.get_full_name() if created_by else 'System',
                'user_role': created_by.role.name if created_by and created_by.role else None,
            })

        data['timeline'] = timeline
        data['lastUpdate'] = ticket.updated_at.isoformat()

        return Response(data)

    except Exception as e:
        print(f"Error in public_ticket_status: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )