# apps/users/mixins.py
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q


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
        
        # ✅ FIX: Select related role and team for better performance
        queryset = User.objects.select_related("team", "role").all()
        
        # ✅ Get user role name safely
        user_role_name = None
        if user.role:
            if hasattr(user.role, 'name'):
                user_role_name = user.role.name.upper()
            elif isinstance(user.role, str):
                user_role_name = user.role.upper()
        elif hasattr(user, 'role_name') and user.role_name:
            user_role_name = user.role_name.upper()
        
        # ✅ Apply search filter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(full_name__icontains=search)  # ✅ Add full_name search
            )
        
        # ✅ Apply role filter (filter by role name)
        role_name = self.request.query_params.get('role')
        if role_name:
            queryset = queryset.filter(role__name__iexact=role_name)
        
        # ✅ Apply team filter
        team_id = self.request.query_params.get('team')
        if team_id:
            try:
                queryset = queryset.filter(team_id=int(team_id))
            except (TypeError, ValueError):
                pass
        
        # =========================
        # ADMIN - Can see all users
        # =========================
        if user_role_name == "ADMIN":
            return queryset
        
        # =========================
        # TEAM_LEAD - Can see AGENT and SUPPORT in their team
        # =========================
        elif user_role_name == "TEAM_LEAD":
            if user.team_id:
                # ✅ FIX: Include both AGENT and SUPPORT roles
                return queryset.filter(
                    team_id=user.team_id,
                    role__name__in=["AGENT", "SUPPORT"]
                )
            return User.objects.none()
        
        # =========================
        # AGENT - Can only see themselves
        # =========================
        elif user_role_name == "AGENT":
            return queryset.filter(id=user.id)
        
        # =========================
        # SUPPORT - Can only see themselves
        # =========================
        elif user_role_name == "SUPPORT":
            return queryset.filter(id=user.id)
        
        # =========================
        # DEFAULT - No access
        # =========================
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