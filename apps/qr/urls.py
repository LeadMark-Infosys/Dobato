from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QRViewSet, QRAnalyticsViewSet

router = DefaultRouter()
router.register(r'', QRViewSet, basename='qr')
router.register(r'qr-analytics', QRAnalyticsViewSet, basename='qranalytics')

urlpatterns = [
    path('', include(router.urls)),
]
