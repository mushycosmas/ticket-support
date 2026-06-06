from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.contrib.auth import get_user_model

from ..models.ticket import Ticket
from ..models.customer import Customer
from ..serializers import TicketSerializer

User = get_user_model()


class CustomerViewSet(viewsets.GenericViewSet):
    """
    Read-only ViewSet for Customers
    Customers are automatically created when tickets are created
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get customers based on user role"""
        user = self.request.user
        
        # Admin can see all customers
        if user.role == 'ADMIN':
            return Customer.objects.all()
        
        # Team Lead can see customers from their team's tickets
        elif user.role == 'TEAM_LEAD':
            return Customer.objects.filter(
                tickets__team_id=user.team_id
            ).distinct()
        
        # Agent can see customers from their assigned tickets
        elif user.role == 'AGENT':
            return Customer.objects.filter(
                tickets__assigned_to=user
            ).distinct()
        
        return Customer.objects.none()
    
    def list(self, request):
        """List all customers"""
        customers = self.get_queryset()
        
        # Apply search filter
        search = request.query_params.get('search', '')
        if search:
            customers = customers.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(company_name__icontains=search)
            )
        
        # Ordering
        order_by = request.query_params.get('order_by', '-created_at')
        customers = customers.order_by(order_by)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        # Prepare customer data with stats
        customer_data = []
        for customer in customers[start:end]:
            customer_data.append({
                'id': customer.id,
                'full_name': customer.full_name,
                'email': customer.email,
                'phone': customer.phone,
                'alternate_phone': customer.alternate_phone,
                'company_name': customer.company_name,
                'address': customer.address,
                'city': customer.city,
                'country': customer.country,
                'total_tickets': customer.total_tickets,
                'total_resolved': customer.total_resolved,
                'total_open': customer.total_open,
                'last_ticket_created': customer.last_ticket_created,
                'created_at': customer.created_at,
            })
        
        return Response({
            'count': customers.count(),
            'page': page,
            'page_size': page_size,
            'results': customer_data
        })
    
    def retrieve(self, request, pk=None):
        """Get single customer with their tickets"""
        try:
            customer = self.get_queryset().get(id=pk)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all tickets for this customer
        tickets = Ticket.objects.filter(customer=customer).order_by('-created_at')
        
        # Apply status filter
        status_filter = request.query_params.get('status')
        if status_filter:
            tickets = tickets.filter(status=status_filter.upper())
        
        # Apply priority filter
        priority_filter = request.query_params.get('priority')
        if priority_filter:
            tickets = tickets.filter(priority=priority_filter.upper())
        
        # Pagination for tickets
        page = int(request.query_params.get('ticket_page', 1))
        page_size = int(request.query_params.get('ticket_page_size', 10))
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_tickets = tickets[start:end]
        
        customer_data = {
            'id': customer.id,
            'full_name': customer.full_name,
            'email': customer.email,
            'phone': customer.phone,
            'alternate_phone': customer.alternate_phone,
            'company_name': customer.company_name,
            'address': customer.address,
            'city': customer.city,
            'country': customer.country,
            'total_tickets': customer.total_tickets,
            'total_resolved': customer.total_resolved,
            'total_open': customer.total_open,
            'last_ticket_created': customer.last_ticket_created,
            'created_at': customer.created_at,
            'updated_at': customer.updated_at,
            'tickets': {
                'count': tickets.count(),
                'page': page,
                'page_size': page_size,
                'results': TicketSerializer(paginated_tickets, many=True).data
            }
        }
        
        return Response(customer_data)
    
    @action(detail=True, methods=['get'])
    def tickets(self, request, pk=None):
        """Get tickets for a specific customer"""
        try:
            customer = self.get_queryset().get(id=pk)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        tickets = Ticket.objects.filter(customer=customer).order_by('-created_at')
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            tickets = tickets.filter(status=status_filter.upper())
        
        priority_filter = request.query_params.get('priority')
        if priority_filter:
            tickets = tickets.filter(priority=priority_filter.upper())
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_tickets = tickets[start:end]
        serializer = TicketSerializer(paginated_tickets, many=True)
        
        return Response({
            'count': tickets.count(),
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search customers by name, email, or phone"""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {"error": "Search query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        customers = self.get_queryset().filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(company_name__icontains=query)
        )
        
        customer_data = [{
            'id': c.id,
            'full_name': c.full_name,
            'email': c.email,
            'phone': c.phone,
            'company_name': c.company_name,
            'total_tickets': c.total_tickets,
        } for c in customers]
        
        return Response(customer_data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get customer statistics"""
        customers = self.get_queryset()
        
        stats = {
            'total_customers': customers.count(),
            'total_tickets': sum(c.total_tickets for c in customers),
            'total_resolved': sum(c.total_resolved for c in customers),
            'total_open': sum(c.total_open for c in customers),
            'customers_with_tickets': customers.filter(total_tickets__gt=0).count(),
        }
        
        return Response(stats)