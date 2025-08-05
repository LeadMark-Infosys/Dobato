from django.db import models
from django.conf import settings
from apps.municipality.models import Municipality
import uuid

class QR(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='qr_app_models' 
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    entity_type = models.CharField(
        max_length=50,
        choices=[
            ('place', 'Place'),
            ('event', 'Event'),
            ('feedback', 'Feedback'),
        ],
        default='feedback'
    )
    entity_id = models.UUIDField()
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    total_scans = models.PositiveIntegerField(default=0)
    unique_ip_count = models.PositiveIntegerField(default=0)
    last_scanned = models.DateTimeField(blank=True, null=True)  
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qr_app_qrs'  
    )
    def __str__(self):
        return f"{self.name} ({self.municipality.name})"
