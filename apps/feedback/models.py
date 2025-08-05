import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.municipality.models import MunicipalityAwareModel

User = get_user_model()

class Feedback(MunicipalityAwareModel):
    feedback_category = [
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('inquiry', 'Inquiry'),
        ('feedback', 'Feedback'),
    ]

    STATUS_CHOICES = [
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
        ('flagged', 'Flagged'),
     ]
    feedback_type = models.CharField(max_length=20, choices=feedback_category, default='feedback')
    title = models.CharField(max_length=200)
    description = models.TextField() 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_review')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_feedbacks')
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='en')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_feedbacks')
    approved_at = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_feedbacks')
    submitted_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.approved_by and self.approved_by.user_type != 'municipality_admin':
            raise ValidationError("Only municipality_admin can approve feedback.")
    def __str__(self):
        return f"{self.title} ({self.municipality.name})"

class FeedbackMedia(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='attachments')
    file = models.TextField() 
    def __str__(self):
        return f"Attachment for feedback {self.feedback.id}"