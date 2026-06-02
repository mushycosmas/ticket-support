from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from .models import Ticket
from .serializers import TicketSerializer

User = get_user_model()


class TicketViewSet(viewsets.ModelViewSet):

    serializer_class = TicketSerializer

    # =========================
    # QUERYSET (ROLE BASED)
    # =========================
    def get_queryset(self):
        user = self.request.user

        queryset = Ticket.objects.select_related(
            "team",
            "assigned_to"
        ).order_by("-id")

        if not user or not user.is_authenticated:
            return Ticket.objects.none()

        # ------------------------
        # ROLE BASE FILTER
        # ------------------------
        if user.role == "ADMIN":
            qs = queryset

        elif user.role == "TEAM_LEAD":
            qs = queryset.filter(team_id=user.team_id) if user.team_id else Ticket.objects.none()

        elif user.role == "AGENT":
            qs = queryset.filter(assigned_to=user)

        else:
            return Ticket.objects.none()

        # ------------------------
        # EXTRA FILTER (FRONTEND CONTROL)
        # ------------------------
        filter_type = self.request.query_params.get("filter")

        if filter_type == "my":
            qs = qs.filter(created_by=user)

        elif filter_type == "assigned":
            qs = qs.exclude(assigned_to=None)

        elif filter_type == "unassigned":
            qs = qs.filter(assigned_to=None)

        elif filter_type == "closed":
            qs = qs.filter(status="CLOSED")

        return qs

      

    # =========================
    # ASSIGN TICKET (ADMIN + TEAM LEAD)
    # =========================
    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):

        user = request.user
        ticket = self.get_object()

        agent_id = request.data.get("assigned_to")
        team_id = request.data.get("team_id")

        # MUST HAVE AT LEAST ONE
        if not agent_id and not team_id:
            return Response(
                {"error": "assigned_to or team_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # =========================
        # ADMIN CAN ASSIGN ANYTHING
        # =========================
        if user.role == "ADMIN":

            # ASSIGN TO TEAM
            if team_id:
                ticket.team_id = team_id
                ticket.assigned_to = None
                ticket.status = "OPEN"
                ticket.save()

                return Response({
                    "message": "Ticket assigned to team",
                    "team_id": ticket.team_id,
                    "status": ticket.status
                })

            # ASSIGN TO AGENT
            if agent_id:
                try:
                    agent = User.objects.get(id=int(agent_id), role="AGENT")
                except User.DoesNotExist:
                    return Response(
                        {"error": "Invalid agent"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                ticket.assigned_to = agent
                ticket.status = "IN_PROGRESS"
                ticket.save()

                return Response({
                    "message": "Ticket assigned to agent",
                    "assigned_to": agent.id,
                    "status": ticket.status
                })

        # =========================
        # TEAM LEAD (ONLY AGENT IN TEAM)
        # =========================
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

            try:
                agent = User.objects.get(id=int(agent_id), role="AGENT")
            except User.DoesNotExist:
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
            ticket.status = "IN_PROGRESS"
            ticket.save()

            return Response({
                "message": "Ticket assigned successfully",
                "assigned_to": agent.id,
                "status": ticket.status
            })

        return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

    # =========================
    # RESOLVE (AGENT OWNER ONLY)
    # =========================
    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):

        user = request.user
        ticket = self.get_object()

        if not user or not user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)

        if user.role == "AGENT":
            if ticket.assigned_to_id != user.id:
                return Response(
                    {"error": "Not your ticket"},
                    status=status.HTTP_403_FORBIDDEN
                )

        ticket.status = "RESOLVED"
        ticket.save()

        return Response({
            "message": "Ticket resolved",
            "status": ticket.status
        })

    # =========================
    # CLOSE (ADMIN + TEAM LEAD)
    # =========================
    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):

        user = request.user
        ticket = self.get_object()

        if not user or not user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)

        if user.role not in ["ADMIN", "TEAM_LEAD"]:
            return Response(
                {"error": "Not allowed"},
                status=status.HTTP_403_FORBIDDEN
            )

        ticket.status = "CLOSED"
        ticket.save()

        return Response({
            "message": "Ticket closed",
            "status": ticket.status
        })