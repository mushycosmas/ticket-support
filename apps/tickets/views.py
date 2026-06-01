from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Ticket
from .serializers import TicketSerializer
from .services import TicketWorkflow


class TicketViewSet(viewsets.ModelViewSet):

    queryset = Ticket.objects.all().order_by('-id')
    serializer_class = TicketSerializer

    # ======================
    # CUSTOM ACTIONS (WORKFLOW)
    # ======================

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        agent = request.data.get("agent")

        TicketWorkflow.assign(ticket, agent)
        return Response({"message": "Ticket assigned", "status": ticket.status})

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        ticket = self.get_object()
        TicketWorkflow.start_progress(ticket)
        return Response({"message": "Work started", "status": ticket.status})

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        TicketWorkflow.resolve(ticket)
        return Response({"message": "Ticket resolved", "status": ticket.status})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        ticket = self.get_object()
        TicketWorkflow.close(ticket)
        return Response({"message": "Ticket closed", "status": ticket.status})