from django.db import models
from apps.municipality.models import Municipality
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import uuid

User = get_user_model()

class FeedbackCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class FeedbackStatus(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    name = models.CharField(max_length=20, choices=STATUS_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.get_name_display()
    
class Feedback(models.Model):
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name='feedbacks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(FeedbackCategory, on_delete=models.SET_NULL, null=True, related_name='feedbacks')
    status = models.ForeignKey(FeedbackStatus, on_delete=models.SET_NULL, null=True, related_name='feedbacks')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_feedbacks')
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_feedbacks')
    approved_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    def clean(self):
        if self.approved_by and self.approved_by.user_type != 'municipality_admin':
            raise ValidationError("Only municipality_admin can approve feedback.")

    def __str__(self):
        return f"{self.title} ({self.municipality.name})"

class FeedbackResponse(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.responder and self.responder.user_type != 'municipality_admin':
            raise ValidationError("Only municipality_admin can respond to feedback.")

    def __str__(self):
        return f"Response by {self.responder} on {self.created_at}"

class Attachment(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='feedback_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for feedback {self.feedback.id}"

class QR(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name='qr_codes')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    entity_type = models.CharField(max_length=50, choices=[
        ('place', 'Place'),
        ('event', 'Event'),
        ('feedback', 'Feedback'),
    ], default='feedback')
    entity_id = models.UUIDField()
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    total_scans = models.PositiveIntegerField(default=0)
    unique_ip_count = models.PositiveIntegerField(default=0)
    last_scanned = models.DateTimeField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.municipality.name})"
