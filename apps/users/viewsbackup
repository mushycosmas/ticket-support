from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Team
from .serializers import (
    UserSerializer, TeamSerializer, 
    UserCreateSerializer, UserUpdateSerializer,
    UserTicketSerializer, UserStatsSerializer
)
from apps.tickets.models import Ticket


# =========================
# USER MANAGEMENT
# =========================
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management
    """
    serializer_class = UserSerializer

    # =========================
    # PERMISSIONS
    # =========================
    def get_permissions(self):
        """
        - Public can CREATE (register)
        - Others require authentication
        """
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'tickets':
            return UserTicketSerializer
        return UserSerializer

    # =========================
    # QUERYSET RULES (ROLE BASED)
    # =========================
    def get_queryset(self):
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

        # ADMIN → ALL USERS
        if user.role == "ADMIN":
            return queryset

        # TEAM LEAD → ONLY TEAM AGENTS
        if user.role == "TEAM_LEAD":
            return queryset.filter(
                team=user.team,
                role="AGENT"
            )

        # AGENT → ONLY SELF
        if user.role == "AGENT":
            return queryset.filter(id=user.id)

        return User.objects.none()

    def list(self, request, *args, **kwargs):
        """List all users with pagination"""
        queryset = self.get_queryset()
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_queryset = queryset[start:end]
        serializer = self.get_serializer(paginated_queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """Create a new user (public registration)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Update a user"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check permission
        if request.user.role != 'ADMIN' and request.user.id != instance.id:
            return Response(
                {"error": "You don't have permission to update this user"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(UserSerializer(user).data)

    def destroy(self, request, *args, **kwargs):
        """Delete a user"""
        user = self.get_object()
        
        # Check permission
        if request.user.role != 'ADMIN':
            return Response(
                {"error": "Only administrators can delete users"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Don't allow deleting yourself
        if user.id == request.user.id:
            return Response(
                {"error": "You cannot delete your own account"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.delete()
        return Response(
            {"message": "User deleted successfully"},
            status=status.HTTP_200_OK
        )

    # =========================
    # GET USER'S TICKETS
    # =========================
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def tickets(self, request, pk=None):
        """Get tickets assigned to a specific user"""
        user = self.get_object()
        
        # Check permission
        if request.user.role != 'ADMIN' and request.user.id != user.id:
            return Response(
                {"error": "You don't have permission to view these tickets"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tickets = Ticket.objects.filter(assigned_to=user).order_by('-created_at')
        
        # Apply status filter
        status_filter = request.query_params.get('status')
        if status_filter:
            tickets = tickets.filter(status=status_filter.upper())
        
        # Apply priority filter
        priority_filter = request.query_params.get('priority')
        if priority_filter:
            tickets = tickets.filter(priority=priority_filter.upper())
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_tickets = tickets[start:end]
        serializer = UserTicketSerializer(paginated_tickets, many=True)
        
        return Response({
            'count': tickets.count(),
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })

    # =========================
    # GET USER'S STATS
    # =========================
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request, pk=None):
        """Get statistics for a user's assigned tickets"""
        user = self.get_object()
        
        # Check permission
        if request.user.role != 'ADMIN' and request.user.id != user.id:
            return Response(
                {"error": "You don't have permission to view these stats"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tickets = Ticket.objects.filter(assigned_to=user)
        
        stats_data = {
            'total_assigned': tickets.count(),
            'total_open': tickets.filter(status='OPEN').count(),
            'total_in_progress': tickets.filter(status='IN_PROGRESS').count(),
            'total_resolved': tickets.filter(status='RESOLVED').count(),
            'total_closed': tickets.filter(status='CLOSED').count(),
        }
        
        serializer = UserStatsSerializer(stats_data)
        return Response(serializer.data)

    # =========================
    # RESET PASSWORD
    # =========================
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def reset_password(self, request, pk=None):
        """Reset user password to default"""
        user = self.get_object()
        
        # Check permission
        if request.user.role != 'ADMIN':
            return Response(
                {"error": "Only administrators can reset passwords"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        default_password = "support123"
        user.set_password(default_password)
        user.save()

        return Response({
            "message": f"Password reset to {default_password}"
        }, status=status.HTTP_200_OK)


# =========================
# TEAM MANAGEMENT
# =========================
class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for Team management"""
    
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'ADMIN':
            return Team.objects.all()
        elif user.role == 'TEAM_LEAD':
            return Team.objects.filter(id=user.team_id)
        else:
            return Team.objects.filter(id=user.team_id) if user.team_id else Team.objects.none()
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all members of a team"""
        team = self.get_object()
        members = User.objects.filter(team=team)
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)


# =========================
# LOGIN API (JWT)
# =========================
class LoginView(APIView):
    """Login endpoint for JWT authentication"""
    
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {"detail": "User account is disabled"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "team_id": user.team.id if user.team else None,
                "team_name": user.team.name if user.team else None,
                "is_active": user.is_active
            }
        })