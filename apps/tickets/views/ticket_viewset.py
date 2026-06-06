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
            "team", "assigned_to", "assigned_by", "customer", "street"
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
        
        print("\n========== CREATING TICKET ==========")
        print("Request data:", request.data)
        
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
            )
            print(f"Customer {'created' if created else 'retrieved'}: {customer}")
        
        # Get fields from request
        street_id = request.data.get('street_id')
        assigned_to_id = request.data.get('assigned_to')
        assigned_by_id = request.data.get('assigned_by')
        team_id = request.data.get('team')
        
        print(f"Assigned to ID: {assigned_to_id}")
        print(f"Assigned by ID: {assigned_by_id}")
        print(f"Team ID: {team_id}")
        
        # Generate ticket number
        ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        
        # Create ticket with basic fields
        ticket = Ticket.objects.create(
            ticket_number=ticket_number,
            title=request.data.get('title'),
            description=request.data.get('description', ''),
            priority=request.data.get('priority', 'MEDIUM'),
            status='OPEN',
            channel=request.data.get('channel', 'WEB'),
            customer=customer,
            street_id=street_id if street_id else None,
        )
        
        # Handle assignment fields
        if assigned_to_id:
            try:
                agent = User.objects.get(id=assigned_to_id)
                ticket.assigned_to = agent
                ticket.status = 'IN_PROGRESS'  # Set to IN_PROGRESS when assigned
                print(f"Assigned to agent: {agent.username}")
            except User.DoesNotExist:
                print(f"Agent with ID {assigned_to_id} not found")
        
        if assigned_by_id:
            try:
                assigned_by_user = User.objects.get(id=assigned_by_id)
                ticket.assigned_by = assigned_by_user
                print(f"Assigned by: {assigned_by_user.username}")
            except User.DoesNotExist:
                print(f"User with ID {assigned_by_id} not found")
        elif request.user and request.user.is_authenticated:
            ticket.assigned_by = request.user
            print(f"Assigned by (current user): {request.user.username}")
        
        if team_id:
            ticket.team_id = team_id
            print(f"Team ID set: {team_id}")
        
        ticket.save()
        
        # Log creation
        TicketHistory.objects.create(
            ticket=ticket,
            action=TicketHistory.ActionType.CREATED,
            created_by=request.user if request.user.is_authenticated else None,
            metadata={
                'title': ticket.title, 
                'description': ticket.description,
                'street_id': street_id,
                'assigned_to': assigned_to_id,
                'assigned_by': assigned_by_id,
                'team_id': team_id
            }
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
                'user_role': history.created_by.role if history.created_by else None,
                'old_status': history.old_status,
                'new_status': history.new_status,
                'old_priority': history.old_priority,
                'new_priority': history.new_priority,
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
            action=TicketHistory.ActionType.RESOLVED,
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
            action=TicketHistory.ActionType.CLOSED,
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
                action=TicketHistory.ActionType.ASSIGNED,
                old_assignee=str(old_assignee) if old_assignee else None,
                new_assignee=agent.get_full_name() or agent.username,
                created_by=request.user,
                metadata={'agent_id': agent.id}
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
            action=TicketHistory.ActionType.COMMENTED,
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