from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

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

    # =========================
    # ROLE HANDLING WITH FOREIGN KEY
    # =========================
    def get_user_role(self, user):
        """Get user role name from role foreign key"""
        if not user or not user.is_authenticated:
            return None
        
        # Check if user has role attribute (foreign key)
        if hasattr(user, 'role') and user.role:
            # If role is a foreign key object, get its name
            if hasattr(user.role, 'name'):
                return user.role.name.upper()
            # If role is a string (fallback)
            elif isinstance(user.role, str):
                return user.role.upper()
        
        # Check if user has role_name attribute (if you added it)
        if hasattr(user, 'role_name') and user.role_name:
            return user.role_name.upper()
            
        return None

    def get_queryset(self):
        user = self.request.user

        if not user or not user.is_authenticated:
            return Ticket.objects.none()

        role = self.get_user_role(user)

        queryset = Ticket.objects.select_related(
            "team", "assigned_to", "assigned_by", "customer", "street"
        ).prefetch_related("attachments", "histories").order_by("-id")

        # ADMIN sees all
        if role == "ADMIN":
            return queryset

        # TEAM LEAD sees team tickets
        elif role == "TEAM_LEAD":
            return queryset.filter(team_id=user.team_id)

        # AGENT sees unassigned + assigned to them
        elif role == "AGENT":
            return queryset.filter(
                Q(assigned_to=user) |
                Q(assigned_to__isnull=True)
            )
        
        # MANAGER sees their team's tickets
        elif role == "MANAGER":
            return queryset.filter(team_id=user.team_id)

        return Ticket.objects.none()

    def list(self, request, *args, **kwargs):
        """List tickets with filters"""
        queryset = self.get_queryset()

        filter_type = request.query_params.get('filter')

        if filter_type == 'my':
            queryset = queryset.filter(assigned_to=request.user)
        elif filter_type == 'assigned':
            queryset = queryset.filter(assigned_to__isnull=False)
        elif filter_type == 'unassigned':
            queryset = queryset.filter(assigned_to__isnull=True)
        elif filter_type == 'closed':
            queryset = queryset.filter(status='CLOSED')

        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())

        priority_filter = request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter.upper())

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 15))
        start = (page - 1) * page_size
        end = start + page_size

        serializer = self.get_serializer(queryset[start:end], many=True)

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

        street_id = request.data.get('street_id')
        assigned_to_id = request.data.get('assigned_to')
        assigned_by_id = request.data.get('assigned_by')
        team_id = request.data.get('team')

        ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"

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

        # Handle assignment
        if assigned_to_id:
            try:
                agent = User.objects.get(id=assigned_to_id)
                ticket.assigned_to = agent
                ticket.status = 'IN_PROGRESS'
            except User.DoesNotExist:
                pass

        if assigned_by_id:
            try:
                assigned_by_user = User.objects.get(id=assigned_by_id)
                ticket.assigned_by = assigned_by_user
            except User.DoesNotExist:
                pass
        elif request.user and request.user.is_authenticated:
            ticket.assigned_by = request.user

        if team_id:
            ticket.team_id = team_id

        ticket.save()

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
        """Get single ticket with timeline"""
        ticket = self.get_object()
        serializer = self.get_serializer(ticket)
        
        # Get the base data
        data = serializer.data
        
        # Build timeline from history
        timeline = []
        for history in ticket.histories.all().order_by('-created_at'):
            # Get user name
            user_name = "System"
            if history.created_by:
                user_name = history.created_by.get_full_name() or history.created_by.username
            
            # Get user role
            user_role = None
            if history.created_by and hasattr(history.created_by, 'role'):
                if history.created_by.role:
                    if hasattr(history.created_by.role, 'name'):
                        user_role = history.created_by.role.name
                    else:
                        user_role = str(history.created_by.role)
            
            # Build message based on action
            message = ""
            if history.action == 'CREATED':
                message = "Ticket created"
            elif history.action == 'ASSIGNED':
                message = f"Assigned to {history.new_assignee}" if history.new_assignee else "Ticket assigned"
            elif history.action == 'COMMENTED':
                message = history.comment or "Comment added"
            elif history.action == 'STATUS_CHANGED':
                message = f"Status changed from {history.old_status} to {history.new_status}"
            elif history.action == 'PRIORITY_CHANGED':
                message = f"Priority changed from {history.old_priority} to {history.new_priority}"
            elif history.action == 'RESOLVED':
                message = "Ticket resolved"
            elif history.action == 'CLOSED':
                message = "Ticket closed"
            elif history.action == 'REOPENED':
                message = "Ticket reopened"
            else:
                message = history.metadata.get('message', f"{history.action}")
            
            timeline.append({
                'id': history.id,
                'date': history.created_at.isoformat(),
                'action': history.action,
                'message': message,
                'type': 'comment' if history.action == 'COMMENTED' else 'update',
                'comment': history.comment,
                'user': user_name,
                'user_role': user_role,
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
        
        # Debug print
        print(f"Timeline count for ticket {ticket.id}: {len(timeline)}")
        if timeline:
            print(f"First timeline item: {timeline[0]}")
        
        return Response(data)
    def _get_display_message(self, history):
        """Get display message for history item"""
        messages = {
            'CREATED': "Ticket created",
            'UPDATED': "Ticket updated",
            'COMMENTED': history.comment or "Comment added",
            'STATUS_CHANGED': f"Status changed from {history.old_status} to {history.new_status}",
            'PRIORITY_CHANGED': f"Priority changed from {history.old_priority} to {history.new_priority}",
            'ASSIGNED': f"Assigned to {history.new_assignee}",
            'UNASSIGNED': f"Unassigned from {history.old_assignee}",
            'RESOLVED': "Ticket resolved",
            'CLOSED': "Ticket closed",
            'REOPENED': "Ticket reopened",
            'ATTACHMENT': "Attachment added",
        }
        return messages.get(history.action, history.metadata.get('message', 'Ticket updated'))
    
    def _get_display_type(self, history):
        """Get display type for history item"""
        type_map = {
            'CREATED': 'info',
            'COMMENTED': 'comment',
            'STATUS_CHANGED': 'update',
            'PRIORITY_CHANGED': 'update',
            'ASSIGNED': 'update',
            'UNASSIGNED': 'update',
            'RESOLVED': 'resolution',
            'CLOSED': 'resolution',
            'ATTACHMENT': 'update',
            'UPDATED': 'update',
            'REOPENED': 'update',
        }
        return type_map.get(history.action, 'info')

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
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
    def reopen(self, request, pk=None):
        ticket = self.get_object()
        comment = request.data.get('comment', '')

        old_status = ticket.status
        ticket.status = 'OPEN'
        ticket.resolved_at = None
        ticket.save()

        TicketHistory.objects.create(
            ticket=ticket,
            action=TicketHistory.ActionType.REOPENED,
            comment=comment,
            old_status=old_status,
            new_status='OPEN',
            created_by=request.user
        )

        return Response({
            'message': 'Ticket reopened successfully',
            'status': ticket.status,
            'comment': comment
        })

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        agent_id = request.data.get('assigned_to')

        if not agent_id:
            return Response(
                {'error': 'assigned_to is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            agent = User.objects.get(id=agent_id)
            
            # Verify agent role
            role_name = None
            if hasattr(agent, 'role') and agent.role:
                if hasattr(agent.role, 'name'):
                    role_name = agent.role.name.upper()
                elif isinstance(agent.role, str):
                    role_name = agent.role.upper()
            elif hasattr(agent, 'role_name'):
                role_name = agent.role_name.upper()
            
            if role_name != 'AGENT':
                return Response(
                    {'error': 'User is not an agent'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            old_assignee = ticket.assigned_to
            old_assignee_name = str(old_assignee) if old_assignee else None
            new_assignee_name = agent.get_full_name() or agent.username
            
            ticket.assigned_to = agent
            ticket.assigned_by = request.user
            ticket.status = 'IN_PROGRESS'
            ticket.save()

            TicketHistory.objects.create(
                ticket=ticket,
                action=TicketHistory.ActionType.ASSIGNED,
                old_assignee=old_assignee_name,
                new_assignee=new_assignee_name,
                created_by=request.user,
                metadata={'agent_id': agent.id}
            )

            return Response({
                'message': 'Ticket assigned successfully',
                'assigned_to': agent.id,
                'assigned_to_name': new_assignee_name,
                'status': ticket.status
            })

        except User.DoesNotExist:
            return Response(
                {'error': 'Agent not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
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
    
    # views.py - Add this to TicketViewSet

@action(detail=False, methods=['get'])
def overdue(self, request):
    """Get tickets that have exceeded more than 2 days"""
    from django.utils import timezone
    from datetime import timedelta
    
    # Calculate the threshold date (2 days ago)
    threshold_date = timezone.now() - timedelta(days=2)
    
    # Get tickets created more than 2 days ago that are not resolved or closed
    overdue_tickets = self.get_queryset().filter(
        created_at__lt=threshold_date
    ).exclude(
        status__in=['RESOLVED', 'CLOSED']
    ).order_by('created_at')
    
    page = self.paginate_queryset(overdue_tickets)
    if page is not None:
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    serializer = self.get_serializer(overdue_tickets, many=True)
    return Response(serializer.data)

@action(detail=False, methods=['get'])
def aging(self, request):
    """Get tickets with aging information"""
    from django.utils import timezone
    from datetime import timedelta
    
    queryset = self.get_queryset().exclude(
        status__in=['RESOLVED', 'CLOSED']
    )
    
    result = []
    for ticket in queryset:
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
    
    # Sort by days old (oldest first)
    result.sort(key=lambda x: x['days_old'], reverse=True)
    
    return Response(result)