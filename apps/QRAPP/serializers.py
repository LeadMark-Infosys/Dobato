from rest_framework import serializers
from .models import QR, QRAnalytics, QRScanSummary

class QRScanSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = QRScanSummary
        fields = '__all__'

class QRSerializer(serializers.ModelSerializer):
    scan_summary = QRScanSummarySerializer(read_only=True)

    class Meta:
        model = QR
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at']

class QRAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRAnalytics
        fields = '__all__'