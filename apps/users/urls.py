# apps/users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, TeamViewSet
from .views.auth_views import (
    LoginView,
    RefreshTokenView,
    VerifyTokenView,
    LogoutView,
    MeView,
)
from .views.profile_views import ChangePasswordView


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'teams', TeamViewSet, basename='team')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh-token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-token/', VerifyTokenView.as_view(), name='verify-token'),
    path('users/update-phone/', UserViewSet.as_view({'patch': 'update_phone'}), name='user-update-phone'),

]