from django.urls import path
from django.http import JsonResponse

urlpatterns = [
    path('', lambda request: JsonResponse({"message": "API working"})),
]