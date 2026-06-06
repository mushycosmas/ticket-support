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
        if user.role != 'ADMIN':
            return Response(
                {"error": "Only administrators can perform this action"},
                status=status.HTTP_403_FORBIDDEN
            )
        return None
    
    def check_self_or_admin(self, user, target_user):
        """Check if user is admin or the target user themselves"""
        if user.role != 'ADMIN' and user.id != target_user.id:
            return Response(
                {"error": "You don't have permission to perform this action"},
                status=status.HTTP_403_FORBIDDEN
            )
        return None