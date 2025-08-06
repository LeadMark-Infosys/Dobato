from rest_framework import serializers
from .models import QR, QRAnalytics, QRScanSummary

class QRSerializer(serializers.ModelSerializer):
    class Meta:
        model = QR
        fields = '__all__'

class QRAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRAnalytics
        fields = '__all__'
        
class QRScanSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = QRScanSummary
        fields = '__all__'
        