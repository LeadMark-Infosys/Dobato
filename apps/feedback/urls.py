from rest_framework import routers
from django.urls import path, include
from .views import (
    FeedbackViewSet, FeedbackCategoryViewSet,
    FeedbackStatusViewSet, FeedbackResponseViewSet,
    AttachmentViewSet, QRViewSet
)

router = routers.DefaultRouter()
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'categories', FeedbackCategoryViewSet)
router.register(r'statuses', FeedbackStatusViewSet)
router.register(r'responses', FeedbackResponseViewSet)
router.register(r'attachments', AttachmentViewSet)
router.register(r'qr-codes', QRViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
