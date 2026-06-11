from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from ..models import Ticket
from ..serializers import TicketSerializer

from ..services.ticket_service import TicketService
from ..queries.ticket_query import TicketQuery
from ..builders.ticket_timeline import TicketTimelineBuilder


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "track"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    # ======================
    # QUERY LAYER
    # ======================
    def get_queryset(self):
        return TicketQuery(self.request).get_queryset()

    # ======================
    # LIST
    # ======================
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = TicketQuery(request).apply_filters(queryset)

        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 15))

        start = (page - 1) * page_size
        end = start + page_size

        serializer = self.get_serializer(queryset[start:end], many=True)

        return Response({
            "count": queryset.count(),
            "page": page,
            "page_size": page_size,
            "results": serializer.data
        })

    # ======================
    # CREATE
    # ======================
    def create(self, request, *args, **kwargs):
        ticket = TicketService.create_ticket(request)
        serializer = self.get_serializer(ticket)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ======================
    # RETRIEVE
    # ======================
    def retrieve(self, request, *args, **kwargs):
        ticket = self.get_object()
        data = self.get_serializer(ticket).data

        data["timeline"] = TicketTimelineBuilder.build(ticket)
        data["lastUpdate"] = ticket.updated_at.isoformat()

        return Response(data)