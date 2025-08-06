from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import QR, QRAnalytics, QRScanSummary
from .serializers import QRSerializer, QRAnalyticsSerializer, QRScanSummarySerializer

class QRViewSet(viewsets.ModelViewSet):
    queryset = QR.objects.all()
    serializer_class = QRSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class QRAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QRAnalytics.objects.all().order_by('-scanned_at')
    serializer_class = QRAnalyticsSerializer

class QRScanSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QRScanSummary.objects.all()
    serializer_class = QRScanSummarySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    