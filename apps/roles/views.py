from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth.models import Permission

from .models import Role
from .serializers import RoleSerializer, PermissionSerializer


# =========================
# ROLE VIEWSET
# =========================
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    @action(detail=False, methods=['get'], url_path='permissions')
    def permissions_list(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='assign-permissions')
    def assign_permissions(self, request, pk=None):
        role = self.get_object()

        permission_ids = request.data.get('permissions', [])
        permissions = Permission.objects.filter(id__in=permission_ids)

        role.permissions.set(permissions)

        return Response({
            "message": "Permissions assigned successfully",
            "role": RoleSerializer(role).data
        })


# =========================
# PERMISSION VIEWSET (FIXED)
# =========================
class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer