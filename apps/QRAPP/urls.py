from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  QRViewSet, QRAnalyticsViewSet, QRScanSummaryViewSet

router = DefaultRouter()
router.register(r'qrs', QRViewSet, basename='qr')
router.register(r'qr-analytics', QRAnalyticsViewSet, basename='qr-analytics')
router.register(r'qr-summaries', QRScanSummaryViewSet, basename='qr-summaries')

urlpatterns = [
    
    path('', include(router.urls)),
]