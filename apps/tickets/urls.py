from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.ticket_viewset import TicketViewSet
from .views.customer_viewset import CustomerViewSet
from .views.public_views import track_ticket, public_ticket_status, test_endpoint

router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'customers', CustomerViewSet, basename='customer')

urlpatterns = [
    # Test endpoint
    path('test/', test_endpoint, name='test'),
    
    # Public tracking endpoints (must come BEFORE router URLs)
    path('tickets/track/', track_ticket, name='track-ticket'),
    path('tickets/track/<str:ticket_number>/', public_ticket_status, name='public-ticket-status'),
    
    # Main API endpoints
    path('', include(router.urls)),
]