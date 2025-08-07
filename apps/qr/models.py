from django.db import models
from django.conf import settings
from apps.municipality.models import Municipality
import uuid
from apps.core.models import BaseModel

class QR(BaseModel):
    ENTITY_TYPE_CHOICES = [
        ('place', 'Place'),
        ('event', 'Event'),
        ('business', 'Business Listing'),
        ('municipality', 'Municipality Profile'),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    entity_type = models.CharField(
        max_length=50,
        choices=ENTITY_TYPE_CHOICES,
    )
    entity_id = models.UUIDField()
    qr_code_image = models.TextField(blank=True, null=True)
    total_scans = models.PositiveIntegerField(default=0)
    unique_ip_count = models.PositiveIntegerField(default=0)
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='created_qrs')
    
    def __str__(self):
        return f"{self.name} ({self.municipality.name})"

class QRAnalytics(BaseModel):
    qr = models.ForeignKey(
        'QR', 
        on_delete=models.CASCADE, 
        related_name='scans_analytics'
    )
    scanned_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.qr.name} scanned at {self.scanned_at} from {self.ip_address}"