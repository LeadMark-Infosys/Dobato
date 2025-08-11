from rest_framework import viewsets
from apps.core.permissions import IsDataEntryOrDataManagerAndApproved
from .models import QR, QRAnalytics
from .serializers import QRSerializer, QRAnalyticsSerializer
from apps.core.views import MunicipalityTenantModelViewSet

class QRViewSet(MunicipalityTenantModelViewSet):
    queryset = QR.objects.all()
    serializer_class = QRSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]


class QRAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = QRAnalytics.objects.all()
    serializer_class = QRAnalyticsSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]
