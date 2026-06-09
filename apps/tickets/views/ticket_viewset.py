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
    # FIXED: PROPER ROLE HANDLING WITH FOREIGN KEY
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
        """Get single ticket"""
        ticket = self.get_object()
        serializer = self.get_serializer(ticket)

        timeline = []
        for history in ticket.histories.all().order_by('created_at'):
            timeline.append({
                'id': history.id,
                'date': history.created_at.isoformat(),
                'action': history.action,
                'comment': history.comment,
                'user': history.created_by.get_full_name() or history.created_by.username if history.created_by else 'System',
                'user_role': history.created_by.role.name if history.created_by and history.created_by.role else None,
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
    def assign(self, request, pk=None):
        ticket = self.get_object()
        agent_id = request.data.get('assigned_to')

        if not agent_id:
            return Response(
                {'error': 'assigned_to is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Check if user has role foreign key with name attribute
            agent = User.objects.get(id=agent_id)
            
            # Verify agent role (assuming role has name attribute)
            if hasattr(agent, 'role') and agent.role:
                if agent.role.name.upper() != 'AGENT':
                    return Response(
                        {'error': 'User is not an agent'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Fallback to role field if it exists
                if getattr(agent, 'role', '').upper() != 'AGENT':
                    return Response(
                        {'error': 'User is not an agent'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

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