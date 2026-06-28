from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Channel
from .serializers import ChannelSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.select_related("team").all().order_by("-id")
    serializer_class = ChannelSerializer
    permission_classes = [AllowAny]