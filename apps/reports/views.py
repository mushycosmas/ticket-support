from rest_framework import viewsets
from .models import KPIReport
from .serializers import KPIReportSerializer


class KPIReportViewSet(viewsets.ModelViewSet):
    queryset = KPIReport.objects.all().order_by('-created_at')
    serializer_class = KPIReportSerializer