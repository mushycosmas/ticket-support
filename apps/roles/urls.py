from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RoleViewSet, PermissionViewSet


router = DefaultRouter()

# Roles API
router.register(r'roles', RoleViewSet, basename='role')

# Permissions API
router.register(r'permissions', PermissionViewSet, basename='permissions')


urlpatterns = [
    path('', include(router.urls)),
]