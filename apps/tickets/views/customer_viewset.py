# apps/tickets/views/customer_viewset.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum

from ..models.customer import Customer
from ..models.ticket import Ticket
from ..serializers import TicketSerializer, CustomerSerializer


class CustomerViewSet(viewsets.GenericViewSet):
    """
    Read-only ViewSet for Customers
    Customers are automatically created when tickets are created
    """
    permission_classes = [IsAuthenticated]

    # =========================
    # QUERYSET BASED ON ROLE (FIXED)
    # =========================
    def get_queryset(self):
        user = self.request.user

        if not user or not user.is_authenticated:
            return Customer.objects.none()

        # Get role name safely (since role is a ForeignKey to Role model)
        role_name = user.role.name if user.role else None

        if role_name == "ADMIN":
            return Customer.objects.all()

        elif role_name == "TEAM_LEAD":
            return Customer.objects.filter(
                tickets__team_id=user.team_id
            ).distinct()

        elif role_name == "AGENT":
            return Customer.objects.filter(
                tickets__assigned_to=user
            ).distinct()

        return Customer.objects.none()

    # =========================
    # LIST CUSTOMERS
    # =========================
    def list(self, request):
        customers = self.get_queryset()

        # Search (including nida_number)
        search = request.query_params.get("search", "")
        if search:
            customers = customers.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(company_name__icontains=search) |
                Q(nida_number__icontains=search)
            )

        # Gender filter
        gender = request.query_params.get("gender")
        if gender:
            customers = customers.filter(gender=gender)

        order_by = request.query_params.get("order_by", "-created_at")
        customers = customers.order_by(order_by)

        # Pagination
        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 20))
        except ValueError:
            page = 1
            page_size = 20

        start = (page - 1) * page_size
        end = start + page_size

        serializer = CustomerSerializer(customers[start:end], many=True)

        return Response({
            "count": customers.count(),
            "page": page,
            "page_size": page_size,
            "results": serializer.data
        })

    # =========================
    # RETRIEVE CUSTOMER
    # =========================
    def retrieve(self, request, pk=None):
        try:
            customer = self.get_queryset().get(id=pk)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        tickets = Ticket.objects.filter(customer=customer).order_by("-created_at")

        status_filter = request.query_params.get("status")
        if status_filter:
            tickets = tickets.filter(status=status_filter.upper())

        priority_filter = request.query_params.get("priority")
        if priority_filter:
            tickets = tickets.filter(priority=priority_filter.upper())

        try:
            page = int(request.query_params.get("ticket_page", 1))
            page_size = int(request.query_params.get("ticket_page_size", 10))
        except ValueError:
            page = 1
            page_size = 10

        start = (page - 1) * page_size
        end = start + page_size

        customer_data = CustomerSerializer(customer).data
        customer_data["tickets"] = {
            "count": tickets.count(),
            "page": page,
            "page_size": page_size,
            "results": TicketSerializer(tickets[start:end], many=True).data
        }

        return Response(customer_data)

    # =========================
    # CUSTOMER TICKETS
    # =========================
    @action(detail=True, methods=["get"])
    def tickets(self, request, pk=None):
        try:
            customer = self.get_queryset().get(id=pk)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        tickets = Ticket.objects.filter(customer=customer).order_by("-created_at")

        status_filter = request.query_params.get("status")
        if status_filter:
            tickets = tickets.filter(status=status_filter.upper())

        priority_filter = request.query_params.get("priority")
        if priority_filter:
            tickets = tickets.filter(priority=priority_filter.upper())

        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 20))
        except ValueError:
            page = 1
            page_size = 20

        start = (page - 1) * page_size
        end = start + page_size

        serializer = TicketSerializer(tickets[start:end], many=True)

        return Response({
            "count": tickets.count(),
            "page": page,
            "page_size": page_size,
            "results": serializer.data
        })

    # =========================
    # SEARCH CUSTOMERS (includes NIDA)
    # =========================
    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "")

        if not query:
            return Response(
                {"error": "Search query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        customers = self.get_queryset().filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(company_name__icontains=query) |
            Q(nida_number__icontains=query)
        )

        serializer = CustomerSerializer(customers[:20], many=True)

        return Response(serializer.data)

    # =========================
    # STATS (OPTIMIZED)
    # =========================
    @action(detail=False, methods=["get"])
    def stats(self, request):
        customers = self.get_queryset()

        stats = customers.aggregate(
            total_customers=Sum("id"),
            total_tickets=Sum("total_tickets"),
            total_resolved=Sum("total_resolved"),
            total_open=Sum("total_open"),
        )

        return Response({
            "total_customers": customers.count(),
            "total_tickets": stats["total_tickets"] or 0,
            "total_resolved": stats["total_resolved"] or 0,
            "total_open": stats["total_open"] or 0,
            "customers_with_tickets": customers.filter(total_tickets__gt=0).count(),
        })