# apps/nida/views.py

import os
import requests

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


NIDA_API_URL = os.getenv(
    "NIDA_API_URL",
    "http://192.168.57.17:83/api/v1/nida"
)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_nida(request):
    """
    Verify NIDA number through external NIDA service.
    Frontend calls Django only.
    """

    nin = request.data.get("nin")

    if not nin:
        return Response(
            {
                "success": False,
                "message": "NIDA number is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        response = requests.post(
            NIDA_API_URL,
            json={
                "nin": nin
            },
            headers={
                "Content-Type": "application/json"
            },
            timeout=10
        )

        return Response(
            response.json(),
            status=response.status_code
        )

    except requests.exceptions.Timeout:
        return Response(
            {
                "success": False,
                "message": "NIDA service timeout"
            },
            status=status.HTTP_504_GATEWAY_TIMEOUT
        )

    except requests.exceptions.RequestException as e:
        return Response(
            {
                "success": False,
                "message": "Unable to connect to NIDA service",
                "error": str(e)
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )