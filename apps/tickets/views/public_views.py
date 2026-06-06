from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..models import Ticket
from ..serializers import TicketSerializer


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
            'track_ticket': 'GET /api/tickets/tickets/track/?ticket_number=XXX'
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def track_ticket(request):
    """Public endpoint to track ticket status"""
    ticket_number = request.query_params.get('ticket_number')
    
    if not ticket_number:
        return Response(
            {'error': 'ticket_number is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        ticket = Ticket.objects.get(ticket_number=ticket_number)
        serializer = TicketSerializer(ticket)
        data = serializer.data
        
        # Add timeline from history (using the correct related_name 'histories')
        timeline = []
        for history in ticket.histories.all().order_by('created_at'):
            timeline.append({
                'id': history.id,
                'date': history.created_at.isoformat(),
                'action': history.action,
                'message': history.display_message,
                'type': history.display_type,
                'comment': history.comment,
                'user': history.created_by.get_full_name() or history.created_by.username if history.created_by else 'System',
                'user_role': history.created_by.role if history.created_by else None,
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
        
    except Ticket.DoesNotExist:
        return Response(
            {'error': f'Ticket "{ticket_number}" not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Error in track_ticket: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def public_ticket_status(request, ticket_number):
    """Alternative public tracking endpoint using URL parameter"""
    try:
        ticket = Ticket.objects.get(ticket_number=ticket_number)
        serializer = TicketSerializer(ticket)
        data = serializer.data
        
        # Add basic timeline
        timeline = []
        for history in ticket.histories.all().order_by('created_at')[:10]:  # Last 10 events
            timeline.append({
                'id': history.id,
                'date': history.created_at.isoformat(),
                'action': history.action,
                'message': history.display_message,
                'type': history.display_type,
                'comment': history.comment,
                'user': history.created_by.get_full_name() or history.created_by.username if history.created_by else 'System',
            })
        
        data['timeline'] = timeline
        data['lastUpdate'] = ticket.updated_at.isoformat()
        
        return Response(data)
    except Ticket.DoesNotExist:
        return Response(
            {'error': f'Ticket "{ticket_number}" not found'},
            status=status.HTTP_404_NOT_FOUND
        )