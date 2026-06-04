from django.shortcuts import render

# DRF imports
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

# Models
from .models import Region, District, Ward, Street

# Serializers
from .serializers import (
    RegionSerializer,
    DistrictSerializer,
    WardSerializer,
    StreetSerializer,
)


# =========================
# REGION (PUBLIC API)
# =========================
class RegionViewSet(ModelViewSet):
    queryset = Region.objects.all().order_by("name")
    serializer_class = RegionSerializer
    permission_classes = [AllowAny]


# =========================
# DISTRICT (PUBLIC API)
# =========================
class DistrictViewSet(ModelViewSet):
    queryset = District.objects.select_related(
        "region"
    ).all().order_by("name")

    serializer_class = DistrictSerializer
    permission_classes = [AllowAny]


# =========================
# WARD (PUBLIC API)
# =========================
class WardViewSet(ModelViewSet):
    queryset = Ward.objects.select_related(
        "district",
        "district__region"
    ).all().order_by("name")

    serializer_class = WardSerializer
    permission_classes = [AllowAny]


# =========================
# STREET (PUBLIC API)
# =========================
class StreetViewSet(ModelViewSet):
    queryset = Street.objects.select_related(
        "ward",
        "ward__district",
        "ward__district__region"
    ).all().order_by("name")

    serializer_class = StreetSerializer
    permission_classes = [AllowAny]