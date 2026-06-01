from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KPIReportViewSet

router = DefaultRouter()
router.register(r'reports', KPIReportViewSet, basename='kpi-report')

urlpatterns = [
    path('', include(router.urls)),
]