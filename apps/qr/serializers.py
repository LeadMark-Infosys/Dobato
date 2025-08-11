from rest_framework import serializers
from .models import QR, QRAnalytics

class QRSerializer(serializers.ModelSerializer):
    class Meta:
        model = QR
        fields = '__all__'

    def create(self, validated_data):
        print("Validated data in create():", validated_data)
        municipality = validated_data.pop('municipality', None)
        print("Municipality popped:", municipality)
        return super().create(validated_data)


class QRAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRAnalytics
        fields = '__all__'

    def validate_ip_address(self, value):
        if not value:
            raise serializers.ValidationError("IP address is required.")
        return value

    def validate(self, attrs):
        qr = attrs.get('qr')
        ip = attrs.get('ip_address')

        if QRAnalytics.objects.filter(qr=qr, ip_address=ip).exists():
          pass 

        return attrs
