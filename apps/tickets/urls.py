from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.customer_viewset import CustomerViewSet
from .views.ticket_viewset import TicketViewSet
from .views.issue_template_view import IssueTemplateViewSet
from .views.public_views import track_ticket, public_ticket_status, test_endpoint

router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'issue-templates', IssueTemplateViewSet, basename='issue-template')

urlpatterns = [
    path('test/', test_endpoint, name='test'),
    path('tickets/track/', track_ticket, name='track-ticket'),
    path('tickets/track/<str:ticket_number>/', public_ticket_status, name='public-ticket-status'),
    path('', include(router.urls)),
]