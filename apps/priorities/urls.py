from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PriorityViewSet

router = DefaultRouter()
router.register(r'', PriorityViewSet, basename="priorities")

urlpatterns = router.urls