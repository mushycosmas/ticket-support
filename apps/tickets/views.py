from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Ticket, TicketAttachment, TicketHistory
from .serializers import TicketSerializer

User = get_user_model()


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    # =========================
    # PERMISSIONS
    # =========================
    def get_permissions(self):
        # Public endpoints (no authentication required)
        if self.action in ["create", "track"]:
            return [AllowAny()]
        # All other actions require authentication
        return [IsAuthenticated()]
    
    # =========================
    # HELPER METHODS
    # =========================
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _log_history(self, ticket, action, user=None, comment=None, 
                     old_status=None, new_status=None, 
                     old_priority=None, new_priority=None,
                     old_assignee=None, new_assignee=None,
                     metadata=None):
        """Helper method to log ticket history"""
        return TicketHistory.objects.create(
            ticket=ticket,
            action=action,
            comment=comment,
            old_status=old_status,
            new_status=new_status,
            old_priority=old_priority,
            new_priority=new_priority,
            old_assignee=old_assignee,
            new_assignee=new_assignee,
            created_by=user,
            ip_address=self._get_client_ip(self.request) if hasattr(self, 'request') else None,
            metadata=metadata or {}
        )

    # =========================
    # CREATE TICKET + FILES
    # =========================
    def create(self, request, *args, **kwargs):
        print("\n========== RAW DATA ==========")
        print(request.data)
        print("\n========== FILES ==========")
        print(request.FILES)

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()

        # Log ticket creation
        user = request.user if request.user.is_authenticated else None
        self._log_history(
            ticket=ticket,
            action=TicketHistory.ActionType.CREATED,
            user=user,
            metadata={'title': ticket.title, 'description': ticket.description}
        )

        # =========================
        # HANDLE ATTACHMENTS SAFELY
        # =========================
        files = request.FILES.getlist("attachments")

        if files:
            print(f"\nSaving {len(files)} attachment(s)...")

            attachments = [
                TicketAttachment(
                    ticket=ticket,
                    file=file,
                    file_name=file.name,
                    uploaded_by=request.user if request.user.is_authenticated else None
                )
                for file in files
            ]

            TicketAttachment.objects.bulk_create(attachments)
            
            # Log attachment addition
            self._log_history(
                ticket=ticket,
                action=TicketHistory.ActionType.ATTACHMENT,
                user=user,
                metadata={'attachments': [f.file_name for f in attachments]}
            )

        return Response(
            self.get_serializer(ticket, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )

    # =========================
    # UPDATE TICKET
    # =========================
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Store old values for comparison
        old_status = instance.status
        old_priority = instance.priority
        old_assigned_to = instance.assigned_to
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()
        
        user = request.user if request.user.is_authenticated else None
        
        # Log status change
        if old_status != ticket.status:
            self._log_history(
                ticket=ticket,
                action=TicketHistory.ActionType.STATUS_CHANGED,
                user=user,
                old_status=old_status,
                new_status=ticket.status,
                metadata={'old_status': old_status, 'new_status': ticket.status}
            )
        
        # Log priority change
        if old_priority != ticket.priority:
            self._log_history(
                ticket=ticket,
                action=TicketHistory.ActionType.PRIORITY_CHANGED,
                user=user,
                old_priority=old_priority,
                new_priority=ticket.priority,
                metadata={'old_priority': old_priority, 'new_priority': ticket.priority}
            )
        
        return Response(serializer.data)

    # =========================
    # QUERYSET
    # =========================
    def get_queryset(self):
        user = self.request.user

        if not user or not user.is_authenticated:
            return Ticket.objects.none()

        queryset = Ticket.objects.select_related(
            "team",
            "assigned_to",
            "assigned_by",
            "street",
            "street__ward",
            "street__ward__district",
            "street__ward__district__region",
        ).prefetch_related(
            "attachments", "histories"
        ).order_by("-id")

        if user.role == "ADMIN":
            qs = queryset

        elif user.role == "TEAM_LEAD":
            qs = queryset.filter(team_id=user.team_id)

        elif user.role == "AGENT":
            qs = queryset.filter(assigned_to=user)

        else:
            return Ticket.objects.none()

        # FILTERS
        filter_type = self.request.query_params.get("filter")

        if filter_type == "my":
            qs = qs.filter(assigned_to=user)

        elif filter_type == "assigned":
            qs = qs.exclude(assigned_to=None)

        elif filter_type == "unassigned":
            qs = qs.filter(assigned_to=None)

        elif filter_type == "closed":
            qs = qs.filter(status="CLOSED")

        street = self.request.query_params.get("street")
        if street:
            qs = qs.filter(street_id=street)

        return qs

    # =========================
    # ADD COMMENT
    # =========================
    @action(detail=True, methods=["post"])
    def add_comment(self, request, pk=None):
        """Add a comment to a ticket"""
        user = request.user
        ticket = self.get_object()
        comment_text = request.data.get("comment")
        
        if not comment_text or not comment_text.strip():
            return Response(
                {"error": "Comment cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        if user.role not in ["ADMIN", "TEAM_LEAD", "AGENT"]:
            return Response(
                {"error": "You don't have permission to comment"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # For agents, check if ticket is assigned to them or their team
        if user.role == "AGENT":
            if ticket.assigned_to_id != user.id and ticket.team_id != user.team_id:
                return Response(
                    {"error": "You can only comment on tickets assigned to you or your team"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Log the comment
        history = self._log_history(
            ticket=ticket,
            action=TicketHistory.ActionType.COMMENTED,
            user=user,
            comment=comment_text,
            metadata={'comment': comment_text}
        )
        
        # Update ticket timestamp
        ticket.save()
        
        return Response({
            "message": "Comment added successfully",
            "comment": {
                "id": history.id,
                "text": comment_text,
                "user": user.get_full_name() or user.username,
                "user_role": user.role,
                "created_at": history.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)

    # =========================
    # ASSIGN TICKET
    # =========================
    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        user = request.user
        ticket = self.get_object()
        
        # Store old assignee for history
        old_assignee = ticket.assigned_to
        old_team = ticket.team_id

        agent_id = request.data.get("assigned_to")
        team_id = request.data.get("team_id")

        if not agent_id and not team_id:
            return Response(
                {"error": "assigned_to or team_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.role == "ADMIN":

            if team_id:
                ticket.team_id = team_id
                ticket.assigned_to = None
                ticket.assigned_by = user
                ticket.status = "OPEN"
                ticket.save()
                
                # Log assignment to team
                self._log_history(
                    ticket=ticket,
                    action=TicketHistory.ActionType.ASSIGNED,
                    user=user,
                    old_assignee=str(old_assignee) if old_assignee else None,
                    new_assignee=f"Team {team_id}",
                    metadata={'team_id': team_id}
                )

                return Response({
                    "message": "Ticket assigned to team",
                    "team_id": ticket.team_id,
                    "status": ticket.status
                })

            if agent_id:
                agent = User.objects.filter(id=agent_id, role="AGENT").first()

                if not agent:
                    return Response(
                        {"error": "Invalid agent"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                ticket.assigned_to = agent
                ticket.assigned_by = user
                ticket.status = "IN_PROGRESS"
                ticket.save()
                
                # Log assignment to agent
                self._log_history(
                    ticket=ticket,
                    action=TicketHistory.ActionType.ASSIGNED,
                    user=user,
                    old_assignee=old_assignee.get_full_name() if old_assignee else None,
                    new_assignee=agent.get_full_name() or agent.username,
                    metadata={'agent_id': agent.id, 'agent_name': agent.get_full_name() or agent.username}
                )

                return Response({
                    "message": "Ticket assigned to agent",
                    "assigned_to": agent.id,
                    "status": ticket.status
                })

        if user.role == "TEAM_LEAD":

            if not user.team_id:
                return Response(
                    {"error": "No team assigned"},
                    status=status.HTTP_403_FORBIDDEN
                )

            if not agent_id:
                return Response(
                    {"error": "assigned_to required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            agent = User.objects.filter(id=agent_id, role="AGENT").first()

            if not agent:
                return Response(
                    {"error": "Invalid agent"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if agent.team_id != user.team_id:
                return Response(
                    {"error": "Not your team agent"},
                    status=status.HTTP_403_FORBIDDEN
                )

            if ticket.team_id != user.team_id:
                return Response(
                    {"error": "Not your team ticket"},
                    status=status.HTTP_403_FORBIDDEN
                )

            ticket.assigned_to = agent
            ticket.assigned_by = user
            ticket.status = "IN_PROGRESS"
            ticket.save()
            
            # Log assignment
            self._log_history(
                ticket=ticket,
                action=TicketHistory.ActionType.ASSIGNED,
                user=user,
                old_assignee=old_assignee.get_full_name() if old_assignee else None,
                new_assignee=agent.get_full_name() or agent.username,
                metadata={'agent_id': agent.id}
            )

            return Response({
                "message": "Ticket assigned successfully",
                "assigned_to": agent.id,
                "status": ticket.status
            })

        return Response(
            {"error": "Not allowed"},
            status=status.HTTP_403_FORBIDDEN
        )

    # =========================
    # RESOLVE TICKET
    # =========================
    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        user = request.user
        ticket = self.get_object()

        if user.role == "AGENT":
            if ticket.assigned_to_id != user.id:
                return Response(
                    {"error": "Not your ticket"},
                    status=status.HTTP_403_FORBIDDEN
                )

        old_status = ticket.status
        ticket.status = "RESOLVED"
        ticket.resolved_at = timezone.now()
        ticket.save()
        
        # Log resolution
        self._log_history(
            ticket=ticket,
            action=TicketHistory.ActionType.RESOLVED,
            user=user,
            old_status=old_status,
            new_status="RESOLVED",
            metadata={'resolved_by': user.get_full_name() or user.username}
        )

        return Response({
            "message": "Ticket resolved",
            "status": ticket.status
        })

    # =========================
    # CLOSE TICKET
    # =========================
    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        user = request.user
        ticket = self.get_object()

        if user.role not in ["ADMIN", "TEAM_LEAD"]:
            return Response(
                {"error": "Not allowed"},
                status=status.HTTP_403_FORBIDDEN
            )

        old_status = ticket.status
        ticket.status = "CLOSED"
        ticket.save()
        
        # Log closing
        self._log_history(
            ticket=ticket,
            action=TicketHistory.ActionType.CLOSED,
            user=user,
            old_status=old_status,
            new_status="CLOSED",
            metadata={'closed_by': user.get_full_name() or user.username}
        )

        return Response({
            "message": "Ticket closed",
            "status": ticket.status
        })
    
    # =========================
    # TRACK TICKET (PUBLIC)
    # =========================
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def track(self, request):
        ticket_number = request.query_params.get("ticket_number")

        if not ticket_number:
            return Response(
                {"error": "ticket_number is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ticket = Ticket.objects.get(ticket_number=ticket_number)
            serializer = self.get_serializer(ticket)
            data = serializer.data
            
            # Build timeline from history
            timeline = []
            for history in ticket.histories.all():
                timeline.append({
                    'id': history.id,
                    'date': history.created_at.isoformat(),
                    'message': history.display_message,
                    'type': history.display_type,
                    'user': history.created_by.get_full_name() or history.created_by.username if history.created_by else 'System',
                    'user_role': history.created_by.role if history.created_by else None,
                    'action': history.action,
                    'is_comment': history.action == TicketHistory.ActionType.COMMENTED,
                    'comment': history.comment if history.action == TicketHistory.ActionType.COMMENTED else None
                })
            
            # Sort oldest first for chronological display
            timeline.sort(key=lambda x: x['date'])
            
            data['timeline'] = timeline
            data['lastUpdate'] = ticket.updated_at.isoformat() if hasattr(ticket, 'updated_at') else ticket.created_at.isoformat()
            
            return Response(data)
        except Ticket.DoesNotExist:
            return Response(
                {"error": "Ticket not found"},
                status=status.HTTP_404_NOT_FOUND
            )