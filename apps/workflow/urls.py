from django.urls import path
from django.http import JsonResponse


def test(request):
    return JsonResponse({"message": "Workflow API working"})


urlpatterns = [
    path('test/', test),
]