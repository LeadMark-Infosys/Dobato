from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QRViewSet, QRAnalyticsViewSet, QRScanSummaryViewSet

router = DefaultRouter()
router.register(r'qr', QRViewSet, basename='qr')
router.register(r'qr-analytics', QRAnalyticsViewSet, basename='qranalytics')
router.register(r'qr-scan-summary', QRScanSummaryViewSet, basename='qrscansummary')

urlpatterns = [
    path('', include(router.urls)),
]
