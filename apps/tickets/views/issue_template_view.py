from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination

from ..models import IssueTemplate
from ..serializers import IssueTemplateSerializer


# ======================
# PAGINATION CLASS
# ======================
class IssueTemplatePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


# ======================
# VIEWSET
# ======================
class IssueTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = IssueTemplateSerializer
    permission_classes = [permissions.AllowAny]  # 👈 make public
    pagination_class = IssueTemplatePagination

    def get_queryset(self):
        return (
            IssueTemplate.objects
            .filter(is_active=True)
            .select_related(
                "category",
                "suggested_priority"
            )
            .prefetch_related(
                "channels"
            )
            .order_by("-created_at")
        )