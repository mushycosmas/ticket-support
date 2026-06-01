from rest_framework import serializers
from .models import KPIReport


class KPIReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPIReport
        fields = '__all__'