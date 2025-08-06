from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import QR, QRAnalytics, QRScanSummary
from .serializers import QRSerializer, QRAnalyticsSerializer, QRScanSummarySerializer

class QRViewSet(viewsets.ModelViewSet):
    queryset = QR.objects.all()
    serializer_class = QRSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
class QRAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = QRAnalytics.objects.all()
    serializer_class = QRAnalyticsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
class QRScanSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QRScanSummary.objects.all()
    serializer_class = QRScanSummarySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
