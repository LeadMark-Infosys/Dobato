from django.db import models
from django.conf import settings
from apps.municipality.models import Municipality
import uuid
from apps.core.models import BaseModel

class QR(BaseModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='qr_codes' 
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    entity_type = models.CharField(
        max_length=50,
        choices=[
            ('place', 'Place'),
            ('event', 'Event'),
            ('feedback', 'Feedback'),
            ('business', 'Business Listing'),
            ('municipality', 'Municipality Profile'),
        ],
        default='feedback'
    )
    entity_id = models.UUIDField()
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_qrs'  
    )
    def __str__(self):
        return f"{self.name} ({self.municipality.name})"

class QRAnalytics(BaseModel):
    qr = models.ForeignKey(
        'QR', 
        on_delete=models.CASCADE, 
        related_name='scans_analytics'
    )
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    scanned_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    approx_location = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return f"{self.qr.name} scanned at {self.scanned_at} from {self.ip_address}"

class QRScanSummary(BaseModel):
    qr = models.OneToOneField(
        'QR', 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='scan_summary'
    )
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    total_scans = models.PositiveIntegerField(default=0)
    unique_ip_count = models.PositiveIntegerField(default=0)
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"Summary for {self.qr.name}: {self.total_scans} scans, last at {self.last_scanned_at}"
