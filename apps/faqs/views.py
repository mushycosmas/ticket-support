from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import F

from .models import FAQ, FAQFeedback
from .serializers import FAQSerializer, FAQFeedbackSerializer


# =========================
# FAQ VIEWSET
# =========================
class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["question", "answer"]
    ordering_fields = ["views", "sort_order", "created_at"]

    # ✅ IMPORTANT: make FAQ PUBLIC for reading
    def get_permissions(self):
        if self.action in ["list", "retrieve", "by_category_channel"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        faq = self.get_object()
        FAQ.objects.filter(id=faq.id).update(views=F("views") + 1)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def by_category_channel(self, request):
        category_id = request.query_params.get("category_id")
        channel_id = request.query_params.get("channel_id")

        qs = self.queryset

        if category_id:
            qs = qs.filter(category_id=category_id)

        if channel_id:
            qs = qs.filter(channel_id=channel_id)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


# =========================
# FAQ FEEDBACK VIEWSET
# =========================
class FAQFeedbackViewSet(viewsets.ModelViewSet):
    queryset = FAQFeedback.objects.all()
    serializer_class = FAQFeedbackSerializer

    # optional but recommended
    permission_classes = [IsAuthenticated]