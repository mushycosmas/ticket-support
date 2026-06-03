from rest_framework import serializers
from .models import Region, District, Ward


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"


# =====================
# DISTRICT FIX
# =====================
class DistrictSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source="region.name", read_only=True)

    class Meta:
        model = District
        fields = ["id", "name", "region", "region_name"]


# =====================
# WARD FIX
# =====================
class WardSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.name", read_only=True)
    region_name = serializers.CharField(source="district.region.name", read_only=True)

    class Meta:
        model = Ward
        fields = ["id", "name", "district", "district_name", "region_name"]