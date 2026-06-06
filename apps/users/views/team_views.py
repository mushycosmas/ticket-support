from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

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
        
        if user.role == 'ADMIN':
            return Team.objects.all()
        elif user.role == 'TEAM_LEAD':
            return Team.objects.filter(id=user.team_id)
        elif user.role == 'AGENT':
            return Team.objects.filter(id=user.team_id) if user.team_id else Team.objects.none()
        return Team.objects.none()
    
    def list(self, request, *args, **kwargs):
        """List all teams with pagination"""
        queryset = self.get_queryset()
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        return self.get_paginated_response(queryset, self.get_serializer_class(), page, page_size)
    
    def create(self, request, *args, **kwargs):
        """Create a new team"""
        error = self.check_admin_permission(request.user)
        if error:
            return error
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.save()
        return Response(TeamSerializer(team).data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update a team"""
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
        """Delete a team"""
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
        members = User.objects.filter(team=team)
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tickets(self, request, pk=None):
        """Get all tickets assigned to a team"""
        team = self.get_object()
        
        status_filter = request.query_params.get('status')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        tickets = Ticket.objects.filter(team=team).order_by('-created_at')
        
        if status_filter:
            tickets = tickets.filter(status=status_filter.upper())
        
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
        
        return Response({
            'total_tickets': tickets.count(),
            'open': tickets.filter(status='OPEN').count(),
            'in_progress': tickets.filter(status='IN_PROGRESS').count(),
            'resolved': tickets.filter(status='RESOLVED').count(),
            'closed': tickets.filter(status='CLOSED').count(),
            'escalated': tickets.filter(status='ESCALATED').count(),
        })