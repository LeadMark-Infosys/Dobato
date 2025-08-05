from django.db import models

from apps.municipality.models import MunicipalityAwareModel
from apps.core.models import BaseModel

class TouristPlace(MunicipalityAwareModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=100)
    tags = models.CharField(max_length=255, blank=True)
    popular_season = models.CharField(max_length=100, blank=True)
    accessibility = models.CharField(max_length=100, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    entry_fee_local = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    entry_fee_foreign = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    opening_hours = models.CharField(max_length=100, blank=True)
    guide_service = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    toilets = models.BooleanField(default=False)
    wifi = models.BooleanField(default=False)
    water = models.BooleanField(default=False)
    electricity = models.BooleanField(default=False)
    font_size_toggle = models.BooleanField(default=False)
    contrast_mode = models.BooleanField(default=False)
    screen_reader_friendly = models.BooleanField(default=False)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    canonical_url = models.URLField(blank=True)
    og_image = models.URLField(blank=True)
    approval_status = models.CharField(max_length=50, default='draft') 
    version = models.PositiveIntegerField(default=1)
    last_edited = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class StorySection(BaseModel):
    place = models.OneToOneField( TouristPlace, on_delete=models.CASCADE)
    short_description = models.TextField()
    full_description = models.TextField()
    timeline = models.TextField(blank=True)
    key_attractions = models.TextField(blank=True)

    def __str__(self):
        return f"Story of {self.place.name}"

class Review(BaseModel):
    place = models.ForeignKey( TouristPlace, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.place.name}"

class Media(models.Model):
    place = models.ForeignKey(TouristPlace, on_delete=models.CASCADE, related_name="media")
    iscover = models.BooleanField(default=False)  
    media_url = models.URLField(blank=True, null=True)
    vr_supported = models.BooleanField(default=False)
   
    def __str__(self):
        return f"Media for {self.place.name}"