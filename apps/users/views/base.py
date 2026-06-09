# apps/users/base.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


class BaseViewSetMixin:
    """Base mixin with common functionality"""
    
    def get_paginated_response(self, queryset, serializer_class, page=1, page_size=20):
        """Helper method for pagination"""
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_queryset = queryset[start:end]
        serializer = serializer_class(paginated_queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'page': page,
            'page_size': page_size,
            'total_pages': (queryset.count() + page_size - 1) // page_size,
            'results': serializer.data
        })
    
    def check_admin_permission(self, user):
        """Check if user is admin"""
        # ✅ FIX: Check role.name instead of role object
        if not user.role or user.role.name != 'ADMIN':
            return Response(
                {"error": "Only administrators can perform this action"},
                status=status.HTTP_403_FORBIDDEN
            )
        return None
    
    def check_team_lead_permission(self, user):
        """Check if user is team lead"""
        # ✅ FIX: Check role.name instead of role object
        if not user.role or user.role.name != 'TEAM_LEAD':
            return Response(
                {"error": "Only team leads can perform this action"},
                status=status.HTTP_403_FORBIDDEN
            )
        return None
    
    def check_agent_permission(self, user):
        """Check if user is agent"""
        # ✅ FIX: Check role.name instead of role object
        if not user.role or user.role.name != 'AGENT':
            return Response(
                {"error": "Only agents can perform this action"},
                status=status.HTTP_403_FORBIDDEN
            )
        return None
    
    def check_self_or_admin(self, user, target_user):
        """Check if user is admin or the target user themselves"""
        # ✅ FIX: Check role.name instead of role object
        is_admin = user.role and user.role.name == 'ADMIN'
        is_self = user.id == target_user.id
        
        if not (is_admin or is_self):
            return Response(
                {"error": "You don't have permission to perform this action"},
                status=status.HTTP_403_FORBIDDEN
            )
        return None
    
    def check_admin_or_team_lead(self, user, team=None):
        """Check if user is admin or team lead of the specified team"""
        is_admin = user.role and user.role.name == 'ADMIN'
        is_team_lead = user.role and user.role.name == 'TEAM_LEAD'
        
        if not (is_admin or is_team_lead):
            return Response(
                {"error": "Only administrators or team leads can perform this action"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # If team is specified, check if team lead owns this team
        if team and is_team_lead and user.team != team:
            return Response(
                {"error": "You can only manage your own team"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return None
    
    def check_team_access(self, user, team):
        """Check if user has access to the team"""
        is_admin = user.role and user.role.name == 'ADMIN'
        is_team_member = user.team == team
        is_team_lead = user.role and user.role.name == 'TEAM_LEAD'
        
        if not (is_admin or is_team_member):
            return Response(
                {"error": "You don't have access to this team"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Team leads can only access their own team
        if is_team_lead and not is_team_member:
            return Response(
                {"error": "You can only access your own team"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return None
    
    def check_user_access(self, user, target_user):
        """Check if user can access target user's data"""
        is_admin = user.role and user.role.name == 'ADMIN'
        is_self = user.id == target_user.id
        is_team_lead = user.role and user.role.name == 'TEAM_LEAD'
        is_same_team = is_team_lead and user.team == target_user.team
        
        if not (is_admin or is_self or is_same_team):
            return Response(
                {"error": "You don't have access to this user's data"},
                status=status.HTTP_403_FORBIDDEN
            )
        return None
    
    def get_user_role_name(self, user):
        """Helper to get user's role name safely"""
        return user.role.name if user.role else None
    
    def has_role(self, user, role_name):
        """Check if user has a specific role"""
        return user.role and user.role.name == role_name
    
    def is_admin(self, user):
        """Check if user is admin"""
        return self.has_role(user, 'ADMIN')
    
    def is_team_lead(self, user):
        """Check if user is team lead"""
        return self.has_role(user, 'TEAM_LEAD')
    
    def is_agent(self, user):
        """Check if user is agent"""
        return self.has_role(user, 'AGENT')