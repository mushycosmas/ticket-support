from rest_framework.permissions import IsAuthenticated, AllowAny

class UserViewSetPermissions:
    """Permission handling for UserViewSet"""
    
    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]


class TeamViewSetPermissions:
    """Permission handling for TeamViewSet"""
    
    def get_permissions(self):
        return [IsAuthenticated()]


class UserQuerySetMixin:
    """Queryset filtering for UserViewSet"""
    
    def get_queryset(self):
        from ..models import User
        
        user = self.request.user
        
        if not user or not user.is_authenticated:
            return User.objects.none()
        
        queryset = User.objects.select_related("team").all()
        
        # Apply search filter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Apply role filter
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Role-based access
        if user.role == "ADMIN":
            return queryset
        elif user.role == "TEAM_LEAD":
            return queryset.filter(team=user.team, role="AGENT")
        elif user.role == "AGENT":
            return queryset.filter(id=user.id)
        
        return User.objects.none()


class TicketStatsMixin:
    """Ticket statistics helper"""
    
    def get_user_ticket_stats(self, user):
        """Get ticket statistics for a user"""
        from apps.tickets.models import Ticket
        
        tickets = Ticket.objects.filter(assigned_to=user)
        
        return {
            'total_assigned': tickets.count(),
            'total_open': tickets.filter(status='OPEN').count(),
            'total_in_progress': tickets.filter(status='IN_PROGRESS').count(),
            'total_resolved': tickets.filter(status='RESOLVED').count(),
            'total_closed': tickets.filter(status='CLOSED').count(),
        }
    
    def get_user_tickets(self, user, status_filter=None, priority_filter=None, page=1, page_size=20):
        """Get paginated tickets for a user"""
        from apps.tickets.models import Ticket
        
        tickets = Ticket.objects.filter(assigned_to=user).order_by('-created_at')
        
        if status_filter:
            tickets = tickets.filter(status=status_filter.upper())
        
        if priority_filter:
            tickets = tickets.filter(priority=priority_filter.upper())
        
        start = (page - 1) * page_size
        end = start + page_size
        
        return tickets[start:end], tickets.count()