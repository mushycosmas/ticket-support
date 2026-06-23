from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.customer_viewset import CustomerViewSet
from .views.ticket_viewset import TicketViewSet
from .views.issue_template_view import IssueTemplateViewSet
from .views.public_views import (
    track_ticket,
    public_ticket_status,
    test_endpoint
)

from .views.ticket_actions import ReturnTicketView  # ✅ ADD THIS


router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'issue-templates', IssueTemplateViewSet, basename='issue-template')


urlpatterns = [
    # ======================
    # TEST
    # ======================
    path('test/', test_endpoint, name='test'),

    # ======================
    # PUBLIC TRACKING
    # ======================
    path('tickets/track/', track_ticket, name='track-ticket'),
    path(
        'tickets/track/<str:ticket_number>/',
        public_ticket_status,
        name='public-ticket-status'
    ),

    # ======================
    # CUSTOM ACTION (RETURN)
    # ======================
    path(
        'tickets/<int:ticket_id>/return/',
        ReturnTicketView.as_view(),
        name='ticket-return'
    ),

    # ======================
    # ROUTER ENDPOINTS
    # ======================
    path('', include(router.urls)),
]