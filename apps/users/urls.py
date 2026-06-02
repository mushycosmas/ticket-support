from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TeamViewSet, LoginView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'teams', TeamViewSet, basename='teams')

urlpatterns = [
    path('', include(router.urls)),

    # 🔥 LOGIN ENDPOINT (THIS FIXES YOUR 404)
    path('login/', LoginView.as_view(), name='login'),
]