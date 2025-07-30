from django.db import models
from apps.municipality.models import MunicipalityAwareModel
from apps.core.models import BaseModel
from django.contrib.auth import get_user_model

class EventCategory(BaseModel):
    name = models.CharField(max_length=100)

class EventLocation(BaseModel):
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    user=models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)

class Event(MunicipalityAwareModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.ForeignKey(EventLocation, on_delete=models.CASCADE)
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    short_summary = models.CharField(max_length=255, blank=True, null=True)
    detailed_description = models.TextField(blank=True, null=True)
    target_audience = models.JSONField(blank=True, null=True)
    REGISTRATION_METHOD_CHOICES=[
        ('online', 'Online'),
        ('walk_in', 'Walk-in'),
        ('email', 'Email'),
        ('phone', 'Phone'),
    ]
    registration_type=models.CharField(max_length=20, choices=REGISTRATION_METHOD_CHOICES, default='online')
    TICKET_PRICE_CHOICES=[
        ('free', 'Free'),
        ('fixed', 'Fixed'),
        ('donation', 'Donation'),
        ('tiered', 'Tiered'),
    ]
    ticket_price=models.CharField(max_length=20, choices=TICKET_PRICE_CHOICES, default='free')
    booking_rsvp_link = models.URLField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    tags = models.JSONField(blank=True, null=True)
    user=models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.title
    
class EventSchedule(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    Max_attendees = models.PositiveIntegerField(blank=True, null=True)
    def __str__(self):
        return f"{self.event.title} - {self.category.name} ({self.start_time} to {self.end_time})" 
    
class OrganizerInfo(BaseModel):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='organizer_info')
    user=models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.name   
    
class EventMedia(BaseModel):
    media_url = models.TextField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='media')
    def __str__(self):
        return f"Media for {self.event.title}"  
  