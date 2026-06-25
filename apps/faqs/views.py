from django.db.models import F
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import FAQ, FAQFeedback
from .serializers import FAQSerializer, FAQFeedbackSerializer


# =========================
# PAGINATION
# =========================
class FAQPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# =========================
# FAQ VIEWSET
# =========================
class FAQViewSet(viewsets.ModelViewSet):
    serializer_class = FAQSerializer
    pagination_class = FAQPagination

    queryset = FAQ.objects.filter(is_active=True)

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "question",
        "answer",
    ]

    ordering_fields = [
        "views",
        "sort_order",
        "created_at",
    ]

    ordering = ["sort_order", "-created_at"]

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
            "by_category_channel",
            "increment_view",
        ]:
            return [AllowAny()]

        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = FAQ.objects.filter(is_active=True)

        category = self.request.query_params.get("category")
        channel = self.request.query_params.get("channel")
        featured = self.request.query_params.get("featured")

        if category:
            queryset = queryset.filter(category_id=category)

        if channel:
            queryset = queryset.filter(channel_id=channel)

        if featured:
            queryset = queryset.filter(is_featured=True)

        return queryset

    # ==================================
    # AUTO INCREMENT ON DETAIL PAGE
    # ==================================
    def retrieve(self, request, *args, **kwargs):
        faq = self.get_object()

        FAQ.objects.filter(pk=faq.pk).update(
            views=F("views") + 1
        )

        faq.refresh_from_db()

        serializer = self.get_serializer(faq)

        return Response(serializer.data)

    # ==================================
    # INCREMENT VIEW MANUALLY
    # ==================================
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[AllowAny],
    )
    def increment_view(self, request, pk=None):
        faq = self.get_object()

        FAQ.objects.filter(pk=faq.pk).update(
            views=F("views") + 1
        )

        faq.refresh_from_db()

        return Response(
            {
                "success": True,
                "views": faq.views,
            },
            status=status.HTTP_200_OK,
        )

    # ==================================
    # CATEGORY + CHANNEL FILTER
    # ==================================
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[AllowAny],
    )
    def by_category_channel(self, request):
        category_id = request.query_params.get("category_id")
        channel_id = request.query_params.get("channel_id")

        queryset = self.get_queryset()

        if category_id:
            queryset = queryset.filter(
                category_id=category_id
            )

        if channel_id:
            queryset = queryset.filter(
                channel_id=channel_id
            )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True
            )
            return self.get_paginated_response(
                serializer.data
            )

        serializer = self.get_serializer(
            queryset,
            many=True
        )

        return Response(serializer.data)


# =========================
# FAQ FEEDBACK VIEWSET
# =========================
class FAQFeedbackViewSet(viewsets.ModelViewSet):
    queryset = FAQFeedback.objects.all()
    serializer_class = FAQFeedbackSerializer
    permission_classes = [IsAuthenticated]