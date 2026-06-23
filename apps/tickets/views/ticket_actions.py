from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from ..models import Ticket, TicketHistory
from apps.users.models import Team


class ReturnTicketView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, ticket_id):
        reason = request.data.get("reason")
        team_id = request.data.get("team_id")

        if not reason:
            return Response(
                {"error": "reason is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ticket = Ticket.objects.select_for_update().get(id=ticket_id)

            # Debug: print current state
            print(f"Ticket {ticket.id}: current team = {ticket.team}, assigned_to = {ticket.assigned_to}")

            old_team = ticket.team
            old_assignee = ticket.assigned_to
            new_team = old_team

            if team_id:
                try:
                    new_team = Team.objects.get(id=team_id)
                    print(f"New team found: {new_team.name} (ID: {new_team.id})")
                except Team.DoesNotExist:
                    return Response(
                        {"error": "Team not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Update ticket
            ticket.team = new_team
            ticket.assigned_to = None
            ticket.status = "RETURNED"
            ticket.save()

            # Convert team objects to strings (e.g., "Admin") or "No Team"
            old_team_str = old_team.name if old_team else "No Team"
            new_team_str = new_team.name if new_team else "No Team"

            # Store history
            TicketHistory.objects.create(
                ticket=ticket,
                action="RETURNED",
                comment=reason,
                old_assignee=str(old_assignee) if old_assignee else None,
                new_assignee=None,
                old_team=old_team_str,
                new_team=new_team_str,
                created_by=request.user,
                metadata={
                    "reason": reason,
                    "team_id": team_id,
                    "old_team_id": old_team.id if old_team else None,
                    "new_team_id": new_team.id if new_team else None,
                }
            )

            return Response({
                "message": "Ticket returned successfully",
                "ticket_id": ticket.id,
                "status": ticket.status
            })

        except Ticket.DoesNotExist:
            return Response(
                {"error": "Ticket not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            print("Return error:", e)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )