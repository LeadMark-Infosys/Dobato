from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    FeedbackViewSet, FeedbackCategoryViewSet,
    QRLocationViewSet, FeedbackStatusViewSet,
    FeedbackResponseViewSet, AttachmentViewSet
)

router = DefaultRouter()
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'categories', FeedbackCategoryViewSet)
router.register(r'qr-locations', QRLocationViewSet)
router.register(r'statuses', FeedbackStatusViewSet)
router.register(r'responses', FeedbackResponseViewSet)
router.register(r'attachments', AttachmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
