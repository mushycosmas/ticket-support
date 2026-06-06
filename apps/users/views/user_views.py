from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import User
from ..serializers import (
    UserSerializer, UserCreateSerializer, 
    UserUpdateSerializer, UserTicketSerializer
)
from .mixins import UserViewSetPermissions, UserQuerySetMixin, TicketStatsMixin
from .base import BaseViewSetMixin


class UserViewSet(
    UserViewSetPermissions,
    UserQuerySetMixin,
    TicketStatsMixin,
    BaseViewSetMixin,
    viewsets.ModelViewSet
):
    serializer_class = UserSerializer
    
    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'tickets':
            return UserTicketSerializer
        return UserSerializer
    
    def list(self, request, *args, **kwargs):
        """List all users with pagination"""
        queryset = self.get_queryset()
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        return self.get_paginated_response(queryset, self.get_serializer_class(), page, page_size)
    
    def create(self, request, *args, **kwargs):
        """Create a new user"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update a user"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check permission
        error = self.check_self_or_admin(request.user, instance)
        if error:
            return error
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a user"""
        user = self.get_object()
        
        # Check admin permission
        error = self.check_admin_permission(request.user)
        if error:
            return error
        
        if user.id == request.user.id:
            return Response(
                {"error": "You cannot delete your own account"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get"])
    def tickets(self, request, pk=None):
        """Get tickets assigned to a user"""
        user = self.get_object()
        
        # Check permission
        error = self.check_self_or_admin(request.user, user)
        if error:
            return error
        
        status_filter = request.query_params.get('status')
        priority_filter = request.query_params.get('priority')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        tickets, total = self.get_user_tickets(user, status_filter, priority_filter, page, page_size)
        serializer = UserTicketSerializer(tickets, many=True)
        
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
            'results': serializer.data
        })
    
    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """Get statistics for a user's tickets"""
        user = self.get_object()
        
        # Check permission
        error = self.check_self_or_admin(request.user, user)
        if error:
            return error
        
        stats = self.get_user_ticket_stats(user)
        return Response(stats)
    
    @action(detail=True, methods=["post"])
    def reset_password(self, request, pk=None):
        """Reset user password"""
        user = self.get_object()
        
        # Check admin permission
        error = self.check_admin_permission(request.user)
        if error:
            return error
        
        default_password = "support123"
        user.set_password(default_password)
        user.save()
        
        return Response(
            {"message": f"Password reset to {default_password}"},
            status=status.HTTP_200_OK
        )