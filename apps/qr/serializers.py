from rest_framework import serializers
from .models import QR, QRAnalytics

class QRSerializer(serializers.ModelSerializer):
    class Meta:
        model = QR
        fields = '__all__'


class QRAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRAnalytics
        fields = '__all__'

    def validate_ip_address(self, value):
        if not value:
            raise serializers.ValidationError("IP address is required.")
        return value
