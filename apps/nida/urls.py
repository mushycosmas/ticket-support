from django.urls import path
from .views import verify_nida

urlpatterns = [
    path("verify/", verify_nida, name="verify-nida"),
]