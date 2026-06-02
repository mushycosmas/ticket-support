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

    # ======================
    # QUERYSET (ROLE BASED)
    # ======================
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
            return queryset.filter(team=user.team)

        # AGENT → ONLY ASSIGNED TICKETS
        if user.role == "AGENT":
            return queryset.filter(assigned_to=user)

        return queryset.none()

    # ======================
    # ASSIGN TICKET
    # ======================
    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):

        ticket = self.get_object()
        agent_id = request.data.get("agent")

        user = request.user

        if not user or not user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        if not agent_id:
            return Response({"error": "agent is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            agent = User.objects.get(id=agent_id, role="AGENT")
        except User.DoesNotExist:
            return Response({"error": "Invalid agent"}, status=status.HTTP_400_BAD_REQUEST)

        # ======================
        # TEAM LEAD RESTRICTIONS
        # ======================
        if user.role == "TEAM_LEAD":

            # must assign within same team
            if agent.team_id != user.team_id:
                return Response(
                    {"error": "You can only assign agents from your team"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # must assign tickets from own team
            if ticket.team_id != user.team_id:
                return Response(
                    {"error": "You can only assign tickets from your team"},
                    status=status.HTTP_403_FORBIDDEN
                )

        TicketWorkflow.assign(ticket, agent)

        return Response({
            "message": "Ticket assigned successfully",
            "status": ticket.status
        })

    # ======================
    # START PROGRESS
    # ======================
    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):

        ticket = self.get_object()

        TicketWorkflow.start_progress(ticket)

        return Response({
            "message": "Work started",
            "status": ticket.status
        })

    # ======================
    # RESOLVE
    # ======================
    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):

        ticket = self.get_object()

        TicketWorkflow.resolve(ticket)

        return Response({
            "message": "Ticket resolved",
            "status": ticket.status
        })

    # ======================
    # CLOSE
    # ======================
    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):

        ticket = self.get_object()

        TicketWorkflow.close(ticket)

        return Response({
            "message": "Ticket closed",
            "status": ticket.status
        })