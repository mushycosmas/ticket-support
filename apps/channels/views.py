from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Channel
from .serializers import ChannelSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing channels.

    Supports:
    - List all channels
    - Retrieve a single channel
    - Create a channel
    - Update a channel
    - Delete a channel
    - Get public channels
    """

    queryset = (
        Channel.objects
        .select_related("team")
        .all()
        .order_by("-id")
    )

    serializer_class = ChannelSerializer
    permission_classes = [AllowAny]

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path="public"
    )
    def public_channels(self, request):
        """
        Return only channels with public status.

        Endpoint:
        GET /api/channels/public/
        """

        channels = (
            Channel.objects
            .select_related("team")
            .filter(status="public")
            .order_by("-id")
        )

        serializer = self.get_serializer(
            channels,
            many=True
        )

        return Response(serializer.data)