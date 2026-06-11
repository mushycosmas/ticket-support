from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # 👈 makes it public