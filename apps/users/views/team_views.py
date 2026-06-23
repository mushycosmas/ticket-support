# apps/users/views/team_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from ..models import Team, User
from ..serializers import TeamSerializer, UserSerializer, UserTicketSerializer
from .mixins import TeamViewSetPermissions, TicketStatsMixin
from .base import BaseViewSetMixin
from apps.tickets.models import Ticket


class TeamViewSet(
    TeamViewSetPermissions,
    TicketStatsMixin,
    BaseViewSetMixin,
    viewsets.ModelViewSet
):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    
    def get_queryset(self):
        user = self.request.user

        if user.role and user.role.name == 'ADMIN':
            return Team.objects.all()

        elif user.role and user.role.name == 'TEAM_LEAD':
            return Team.objects.filter(id=user.team_id)

        elif user.role and user.role.name == 'AGENT':
         return Team.objects.filter(id=user.team_id) if user.team_id else Team.objects.none()

        return Team.objects.none()

    def list(self, request, *args, **kwargs):
        """List all teams with pagination"""
        queryset = self.get_queryset()
        print("kelvin")
        # Apply search filter
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        return self.get_paginated_response(queryset, self.get_serializer_class(), page, page_size)
    
    def retrieve(self, request, *args, **kwargs):
        """Get single team with member count"""
        team = self.get_object()
        serializer = self.get_serializer(team)
        data = serializer.data
        data['member_count'] = team.members.count()
        return Response(data)
    
    def create(self, request, *args, **kwargs):
        """Create a new team - Admin only"""
        error = self.check_admin_permission(request.user)
        if error:
            return error
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.save()
        return Response(TeamSerializer(team).data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update a team - Admin only"""
        error = self.check_admin_permission(request.user)
        if error:
            return error
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        team = serializer.save()
        return Response(TeamSerializer(team).data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a team - Admin only"""
        error = self.check_admin_permission(request.user)
        if error:
            return error
        
        team = self.get_object()
        team.delete()
        return Response({"message": "Team deleted successfully"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all members of a team"""
        team = self.get_object()
        members = team.members.all()
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to the team - Admin or Team Lead only"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        current_user = request.user
        
        # ✅ Check permission based on role name
        is_admin = current_user.role and current_user.role.name == 'ADMIN'
        is_team_lead = current_user.role and current_user.role.name == 'TEAM_LEAD' and current_user.team_id == team.id
        
        if not (is_admin or is_team_lead):
            return Response(
                {"error": "You don't have permission to add members to this team"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            team.members.add(user)
            
            # If user doesn't have a team assigned, set it
            if not user.team:
                user.team = team
                user.save()
            
            return Response({
                "message": f"User {user.get_full_name() or user.username} added to team {team.name}",
                "member_count": team.members.count()
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        """Remove a member from the team - Admin or Team Lead only"""
        team = self.get_object()
        user_id = request.query_params.get('user_id') or request.data.get('user_id')
        current_user = request.user
        
        # ✅ Check permission based on role name
        is_admin = current_user.role and current_user.role.name == 'ADMIN'
        is_team_lead = current_user.role and current_user.role.name == 'TEAM_LEAD' and current_user.team_id == team.id
        
        if not (is_admin or is_team_lead):
            return Response(
                {"error": "You don't have permission to remove members from this team"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            team.members.remove(user)
            
            # If user's team is this team, remove the association
            if user.team == team:
                user.team = None
                user.save()
            
            return Response({
                "message": f"User {user.get_full_name() or user.username} removed from team {team.name}",
                "member_count": team.members.count()
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def tickets(self, request, pk=None):
        """Get all tickets assigned to a team"""
        team = self.get_object()
        
        status_filter = request.query_params.get('status')
        priority_filter = request.query_params.get('priority')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        tickets = Ticket.objects.filter(team=team).order_by('-created_at')
        
        if status_filter:
            tickets = tickets.filter(status=status_filter.upper())
        
        if priority_filter:
            tickets = tickets.filter(priority=priority_filter.upper())
        
        total = tickets.count()
        start = (page - 1) * page_size
        end = start + page_size
        paginated_tickets = tickets[start:end]
        
        serializer = UserTicketSerializer(paginated_tickets, many=True)
        
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get team statistics"""
        team = self.get_object()
        tickets = Ticket.objects.filter(team=team)
        
        # Priority breakdown
        priority_stats = {
            'critical': tickets.filter(priority='CRITICAL').count(),
            'high': tickets.filter(priority='HIGH').count(),
            'medium': tickets.filter(priority='MEDIUM').count(),
            'low': tickets.filter(priority='LOW').count(),
        }
        
        return Response({
            'total_tickets': tickets.count(),
            'open': tickets.filter(status='OPEN').count(),
            'in_progress': tickets.filter(status='IN_PROGRESS').count(),
            'resolved': tickets.filter(status='RESOLVED').count(),
            'closed': tickets.filter(status='CLOSED').count(),
            'escalated': tickets.filter(status='ESCALATED').count(),
            'by_priority': priority_stats
        })
    
    @action(detail=False, methods=['get'])
    def my_team(self, request):
        """Get the current user's team"""
        user = request.user
        
        if not user.team_id:
            return Response(
                {"error": "You are not assigned to any team"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        team = Team.objects.filter(id=user.team_id).first()
        if not team:
            return Response(
                {"error": "Team not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(team)
        data = serializer.data
        data['member_count'] = team.members.count()
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def available_members(self, request):
        """Get users that can be added to a team (no team assigned yet)"""
        current_user = request.user
        
        # Admin can see all users without a team
        if current_user.role and current_user.role.name == 'ADMIN':
            users = User.objects.filter(team__isnull=True)
        else:
            # Team leads can only see agents without a team
            users = User.objects.filter(team__isnull=True, role__name='AGENT')
        
        search = request.query_params.get('search')
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def all_teams(self, request):
        teams = Team.objects.all().order_by("name")

        serializer = TeamSerializer(teams, many=True)

        return Response({
            "count": teams.count(),
            "results": serializer.data
    })