from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models import Ticket, TicketAttachment, TicketHistory
from ..serializers import TicketSerializer

User = get_user_model()


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ["create", "track"]:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        
        if not user or not user.is_authenticated:
            return Ticket.objects.none()
        
        queryset = Ticket.objects.select_related(
            "team", "assigned_to", "assigned_by"
        ).prefetch_related("attachments", "histories").order_by("-id")
        
        if user.role == "ADMIN":
            return queryset
        elif user.role == "TEAM_LEAD":
            return queryset.filter(team_id=user.team_id)
        elif user.role == "AGENT":
            return queryset.filter(assigned_to=user)
        
        return Ticket.objects.none()
    
    def list(self, request, *args, **kwargs):
        """List tickets with filters"""
        queryset = self.get_queryset()
        
        # Apply filters
        filter_type = request.query_params.get('filter')
        
        if filter_type == 'my' and request.user.is_authenticated:
            queryset = queryset.filter(assigned_to=request.user)
        elif filter_type == 'assigned':
            queryset = queryset.exclude(assigned_to=None)
        elif filter_type == 'unassigned':
            queryset = queryset.filter(assigned_to=None)
        elif filter_type == 'closed':
            queryset = queryset.filter(status='CLOSED')
        
        # Status filter
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        
        # Priority filter
        priority_filter = request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter.upper())
        
        # Search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 15))
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_queryset = queryset[start:end]
        serializer = self.get_serializer(paginated_queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """Create a new ticket"""
        import uuid
        from ..models import Customer
        
        # Get or create customer
        email = request.data.get('customer_email')
        phone = request.data.get('customer_phone')
        full_name = request.data.get('customer_name')
        
        customer = None
        if email or phone:
            customer, created = Customer.get_or_create_customer(
                email=email,
                phone=phone,
                full_name=full_name,
                created_by=request.user if request.user.is_authenticated else None
            )
        
        # Generate ticket number
        ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        
        # Create ticket
        ticket = Ticket.objects.create(
            ticket_number=ticket_number,
            title=request.data.get('title'),
            description=request.data.get('description', ''),
            priority=request.data.get('priority', 'P3_MEDIUM'),
            status='OPEN',
            channel='WEB' if request.user.is_authenticated else 'PUBLIC',
            customer=customer,
            created_by=request.user if request.user.is_authenticated else None
        )
        
        # Log creation
        TicketHistory.objects.create(
            ticket=ticket,
            action='CREATED',
            created_by=request.user if request.user.is_authenticated else None,
            metadata={'title': ticket.title}
        )
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """Get single ticket"""
        ticket = self.get_object()
        serializer = self.get_serializer(ticket)
        
        # Add timeline
        timeline = []
        for history in ticket.histories.all().order_by('created_at'):
            timeline.append({
                'id': history.id,
                'date': history.created_at.isoformat(),
                'action': history.action,
                'comment': history.comment,
                'user': history.created_by.get_full_name() or history.created_by.username if history.created_by else 'System',
            })
        
        data = serializer.data
        data['timeline'] = timeline
        data['lastUpdate'] = ticket.updated_at.isoformat()
        
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a ticket"""
        ticket = self.get_object()
        comment = request.data.get('comment', '')
        
        old_status = ticket.status
        ticket.status = 'RESOLVED'
        ticket.resolved_at = timezone.now()
        ticket.save()
        
        TicketHistory.objects.create(
            ticket=ticket,
            action='RESOLVED',
            comment=comment,
            old_status=old_status,
            new_status='RESOLVED',
            created_by=request.user
        )
        
        return Response({
            'message': 'Ticket resolved successfully',
            'status': ticket.status,
            'comment': comment
        })
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a ticket"""
        ticket = self.get_object()
        comment = request.data.get('comment', '')
        
        old_status = ticket.status
        ticket.status = 'CLOSED'
        ticket.save()
        
        TicketHistory.objects.create(
            ticket=ticket,
            action='CLOSED',
            comment=comment,
            old_status=old_status,
            new_status='CLOSED',
            created_by=request.user
        )
        
        return Response({
            'message': 'Ticket closed successfully',
            'status': ticket.status,
            'comment': comment
        })
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign ticket to agent"""
        ticket = self.get_object()
        agent_id = request.data.get('assigned_to')
        
        if not agent_id:
            return Response(
                {'error': 'assigned_to is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            agent = User.objects.get(id=agent_id, role='AGENT')
            old_assignee = ticket.assigned_to
            ticket.assigned_to = agent
            ticket.assigned_by = request.user
            ticket.status = 'IN_PROGRESS'
            ticket.save()
            
            TicketHistory.objects.create(
                ticket=ticket,
                action='ASSIGNED',
                old_assignee=str(old_assignee) if old_assignee else None,
                new_assignee=agent.get_full_name() or agent.username,
                created_by=request.user
            )
            
            return Response({
                'message': 'Ticket assigned successfully',
                'assigned_to': agent.id,
                'assigned_to_name': agent.get_full_name() or agent.username,
                'status': ticket.status
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'Agent not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add comment to ticket"""
        ticket = self.get_object()
        comment = request.data.get('comment')
        
        if not comment:
            return Response(
                {'error': 'Comment is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        history = TicketHistory.objects.create(
            ticket=ticket,
            action='COMMENTED',
            comment=comment,
            created_by=request.user
        )
        
        return Response({
            'message': 'Comment added successfully',
            'comment': {
                'id': history.id,
                'text': comment,
                'user': request.user.get_full_name() or request.user.username,
                'created_at': history.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)