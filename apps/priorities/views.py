from rest_framework.viewsets import ModelViewSet
from .models import Priority
from .serializers import PrioritySerializer

class PriorityViewSet(ModelViewSet):
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer