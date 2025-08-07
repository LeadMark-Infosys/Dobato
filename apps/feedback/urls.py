from rest_framework import routers
from django.urls import path, include
from .views import FeedbackViewSet, MediaViewSet

router = routers.DefaultRouter()
router.register(r'', FeedbackViewSet)
router.register(r'attachments', MediaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
