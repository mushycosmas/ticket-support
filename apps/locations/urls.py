from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, DistrictViewSet, WardViewSet,StreetViewSet

router = DefaultRouter()

router.register(r"regions", RegionViewSet)
router.register(r"districts", DistrictViewSet)
router.register(r"wards", WardViewSet)
router.register(r"streets", StreetViewSet)

urlpatterns = [
    path("", include(router.urls)),
]