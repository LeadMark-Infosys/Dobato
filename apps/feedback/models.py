from django.db import models
from apps.municipality.models import Municipality
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import uuid

User = get_user_model()

class FeedbackCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    name_nepali = models.CharField(max_length=100, blank=True, null=True) 

    def __str__(self):
        return self.name

class FeedbackStatus(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
        ('flagged', 'Flagged'),
    ]
    name = models.CharField(max_length=20, choices=STATUS_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.get_name_display()

class QRLocation(models.Model):
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name='qr_locations')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    qr_code_image = models.CharField(max_length=255, blank=True, null=True)
    target_url = models.URLField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True,)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    last_scanned = models.DateTimeField(null=True, blank=True)
    total_scans = models.PositiveIntegerField(default=0)
    unique_users = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"{self.name} ({self.municipality.name})"

class Feedback(models.Model):
    feedback_type_choices = [
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('inquiry', 'Inquiry'),
        ('feedback', 'Feedback'),
    ]
    tracking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    feedback_type = models.CharField(max_length=20, choices=feedback_type_choices, default='complaint')
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name='feedbacks')
    title = models.CharField(max_length=200)
    description = models.TextField() 
    category = models.ForeignKey(FeedbackCategory, on_delete=models.SET_NULL, null=True, related_name='feedbacks')
    qr_location = models.ForeignKey(QRLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    status = models.ForeignKey(FeedbackStatus, on_delete=models.SET_NULL, null=True, related_name='feedbacks')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_feedbacks')
    submitted_name = models.CharField(max_length=100, blank=True, null=True)
    submitted_email = models.EmailField(blank=True, null=True)
    submitted_phone = models.CharField(max_length=20, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_feedbacks')
    approved_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='en')
    ward = models.CharField(max_length=50, blank=True, null=True)  
    map_pin_lat = models.FloatField(blank=True, null=True)
    map_pin_lng = models.FloatField(blank=True, null=True)
    spam_flag = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    device_info = models.CharField(max_length=255, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    def clean(self):
        if self.approved_by and self.approved_by.user_type != 'municipality_admin':
            raise ValidationError("Only municipality_admin can approve feedback.")
    def __str__(self):
        return f"{self.title} ({self.municipality.name})"

class FeedbackResponse(models.Model):
    RESPONSE_TYPE_CHOICES = [
        ('public', 'Public Response'),
        ('private', 'Private Response'),
        ('internal', 'Internal Note'),
    ]
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    response_type = models.CharField(max_length=10, choices=RESPONSE_TYPE_CHOICES, default='private')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    email_sent = models.BooleanField(default=False)
    public_visible = models.BooleanField(default=False)
    def clean(self):
        if self.responder and self.responder.user_type not in ['municipality_admin', 'department_manager']:
            raise ValidationError("Only municipality_admin or department_manager can respond to feedback.")
    def __str__(self):
        return f"Response by {self.responder} on {self.created_at}"

class Attachment(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='attachments')
    file = models.TextField() 
    def __str__(self):
        return f"Attachment for feedback {self.feedback.id}"

class QRAnalytics(models.Model):
    qr_location = models.ForeignKey(QRLocation, on_delete=models.CASCADE, related_name='analytics')
    entity_type = models.CharField(max_length=50)
    entity_id = models.PositiveIntegerField()
    scan_timestamp = models.DateTimeField(auto_now_add=True)
    device_info = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_unique = models.BooleanField(default=False)
    def __str__(self):
        return f"QR Scan for {self.entity_type} {self.entity_id} at {self.scan_timestamp}"