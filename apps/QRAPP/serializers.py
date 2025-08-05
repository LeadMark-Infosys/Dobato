from rest_framework import serializers
from .models import QR

class QRSerializer(serializers.ModelSerializer):
    class Meta:
        model = QR
        fields = '__all__'
        read_only_fields = ['uuid', 'total_scans', 'unique_ip_count', 'last_scanned']
