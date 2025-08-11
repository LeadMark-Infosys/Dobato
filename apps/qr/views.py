from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.utils.timezone import now
from .models import QR, QRAnalytics
from .serializers import QRSerializer, QRAnalyticsSerializer
from apps.core.views import MunicipalityTenantModelViewSet

class QRViewSet(MunicipalityTenantModelViewSet):
    queryset = QR.objects.all()
    serializer_class = QRSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class QRAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = QRAnalytics.objects.all()
    serializer_class = QRAnalyticsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        qr = serializer.validated_data['qr']
        ip_address = serializer.validated_data['ip_address']
        is_new_ip = not QRAnalytics.objects.filter(qr=qr, ip_address=ip_address).exists()
        serializer.save()
        qr.total_scans += 1
        if is_new_ip:
            qr.unique_ip_count += 1
        qr.last_scanned_at = now()
        qr.save()
