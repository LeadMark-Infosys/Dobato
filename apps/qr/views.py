from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import QR, QRAnalytics
from .serializers import QRSerializer, QRAnalyticsSerializer

class QRViewSet(viewsets.ModelViewSet):
    queryset = QR.objects.all()
    serializer_class = QRSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
class QRAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = QRAnalytics.objects.all()
    serializer_class = QRAnalyticsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]