# apps/roles/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import Permission

from .models import Role
from .serializers import RoleSerializer, PermissionSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    @action(detail=False, methods=['get'], url_path='permissions')
    def permissions_list(self, request):
        """Get all available permissions"""
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='assign-permissions')
    def assign_permissions(self, request, pk=None):
        role = self.get_object()

        permission_ids = request.data.get('permissions', [])

        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.set(permissions)

        serializer = self.get_serializer(role)
        return Response(serializer.data)