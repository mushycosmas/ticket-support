from rest_framework.routers import DefaultRouter
from .views import FAQViewSet, FAQFeedbackViewSet

router = DefaultRouter()
router.register(r"faqs", FAQViewSet, basename="faqs")
router.register(r"faq-feedback", FAQFeedbackViewSet, basename="faq-feedback")

urlpatterns = router.urls