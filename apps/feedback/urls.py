from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import FeedbackViewSet, MediaViewSet

router = DefaultRouter()
router.register(r'', FeedbackViewSet)
router.register(r'attachments', MediaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
