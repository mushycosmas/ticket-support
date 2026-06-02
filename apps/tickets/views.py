from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from .models import Ticket
from .serializers import TicketSerializer
from .services import TicketWorkflow

User = get_user_model()


class TicketViewSet(viewsets.ModelViewSet):

    serializer_class = TicketSerializer

    # =========================
    # ROLE-BASED QUERYSET
    # =========================
    def get_queryset(self):
        user = self.request.user

        queryset = Ticket.objects.select_related(
            "team",
            "assigned_to"
        ).order_by("-id")

        # NOT AUTHENTICATED
        if not user or not user.is_authenticated:
            return Ticket.objects.none()

        # ADMIN → ALL TICKETS
        if user.role == "ADMIN":
            return queryset

        # TEAM LEAD → ONLY TEAM TICKETS
        if user.role == "TEAM_LEAD":
            if user.team_id:
                return queryset.filter(team_id=user.team_id)
            return Ticket.objects.none()

        # AGENT → ONLY ASSIGNED TICKETS
        if user.role == "AGENT":
            return queryset.filter(assigned_to=user)

        return Ticket.objects.none()

    # =========================
    # ASSIGN TICKET
    # =========================
    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):

        user = request.user
        ticket = self.get_object()

        agent_id = request.data.get("assigned_to")
        
      
        # VALIDATION
        if not agent_id:
            return Response(
                {"error": "assigned_to is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # GET AGENT
        try:
            agent = User.objects.get(id=int(agent_id), role="AGENT")
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid agent"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # =========================
        # TEAM LEAD RULES
        # =========================
        if user.role == "TEAM_LEAD":

            # must have team
            if not user.team_id:
                return Response(
                    {"error": "No team assigned"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # agent must be in same team
            if agent.team_id != user.team_id:
                return Response(
                    {"error": "You can only assign agents from your team"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # ticket must belong to same team
            if ticket.team_id != user.team_id:
                return Response(
                    {"error": "You can only assign tickets from your team"},
                    status=status.HTTP_403_FORBIDDEN
                )

        # =========================
        # ASSIGN TICKET
        # =========================
        ticket.assigned_to = agent
        ticket.status = "IN_PROGRESS"
        ticket.save()

        return Response({
            "message": "Ticket assigned successfully",
            "assigned_to": agent.id,
            "status": ticket.status
        })

    # =========================
    # START PROGRESS
    # =========================
    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):

        ticket = self.get_object()
        TicketWorkflow.start_progress(ticket)

        return Response({
            "message": "Work started",
            "status": ticket.status
        })

    # =========================
    # RESOLVE
    # =========================
    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):

        ticket = self.get_object()
        TicketWorkflow.resolve(ticket)

        return Response({
            "message": "Ticket resolved",
            "status": ticket.status
        })

    # =========================
    # CLOSE
    # =========================
    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):

        ticket = self.get_object()
        TicketWorkflow.close(ticket)

        return Response({
            "message": "Ticket closed",
            "status": ticket.status
        })
@action(detail=True, methods=["post"])
def resolve(self, request, pk=None):

    user = request.user
    ticket = self.get_object()

    if not user.is_authenticated:
        return Response({"error": "Unauthorized"}, status=401)

    # AGENT RULE
    if user.role == "AGENT":
        if ticket.assigned_to != user:
            return Response({"error": "Not your ticket"}, status=403)

    ticket.status = "RESOLVED"
    ticket.save()

    return Response({
        "message": "Ticket resolved",
        "status": ticket.status
    })


@action(detail=True, methods=["post"])
def close(self, request, pk=None):

    user = request.user
    ticket = self.get_object()

    if not user.is_authenticated:
        return Response({"error": "Unauthorized"}, status=401)

    # ONLY ADMIN or TEAM LEAD can close
    if user.role not in ["ADMIN", "TEAM_LEAD"]:
        return Response({"error": "Not allowed"}, status=403)

    ticket.status = "CLOSED"
    ticket.save()

    return Response({
        "message": "Ticket closed",
        "status": ticket.status
    })