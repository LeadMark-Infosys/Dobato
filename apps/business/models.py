from django.db import models
from django.contrib.auth import get_user_model
from apps.municipality.models import MunicipalityAwareModel
from apps.core.models import BaseModel

class Business(MunicipalityAwareModel):
    BUSINESS_TYPE_CHOICES = [
        ('Hotel', 'Hotel'),
        ('TravelAgency', 'Travel Agency'),
        ('Restaurant', 'Restaurant'),
        ('TaxiService', 'Taxi Service'),
        ('LocalProduct', 'Local Product'),
        ('Rental', 'Rental'),
        ('GuideAgency', 'Guide Agency'),
    ]
    KEYWORD_CHOICES = [
        ('family_friendly', 'Family-Friendly'),
        ('budget', 'Budget'),
        ('luxury', 'Luxury'),
        ('home_delivery', 'Home Delivery'),
    ]
    BOOKING_METHOD_CHOICES=[
        ('Phone','phone'),
        ('Email','email'),
        ('Whatsapp','whatsapp'),
        ('Instagram','instagram'),
        ('In_Person_website','in_person_website'),
    ]
    STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('archived', 'Archived'),
]
    service_coverage = models.CharField(
        max_length=100,
        choices=[
            ('Local', 'Local area'),
            ('Municipality', 'Full municipality'),
            ('District', 'Entire district')
        ],
        default='Local'
    )

    pricing_type = models.CharField(
        max_length=50,
        choices=[('Fixed', 'Fixed'), ('Range', 'Range')],
        default='Fixed'
    )

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    slug=models.CharField(max_length=50,blank=True,unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    business=models.CharField(max_length=50,choices=BUSINESS_TYPE_CHOICES)
    booking=models.CharField(max_length=50,choices=BOOKING_METHOD_CHOICES)
    short_description=models.CharField(max_length=50)
    full_description=models.TextField()
    user=models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    Established_Date=models.DateTimeField(null=True,blank=True)
    reg_no = models.CharField(max_length=255, unique=True)
    overview = models.TextField()
    history = models.TextField()
    values = models.TextField()
    specialities = models.JSONField(default=list)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    service_offer = models.JSONField(default=list, blank=True)
    fixed_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_range_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_range_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_notes = models.TextField(blank=True)
    extra_travel_fee_notes = models.TextField(blank=True)
    keyword = models.CharField(max_length=50, choices=KEYWORD_CHOICES)
    authorized_person = models.CharField(max_length=255)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    open_days = models.CharField(max_length=100, blank=True, help_text="e.g., Mon-Fri, Everyday, Sat-Sun")
    cover_image = models.TextField()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class BusinessMedia(models.Model):
    media_url = models.TextField()
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='gallery')
    def __str__(self):
        return f"Media for {self.business.name}"

class Review(BaseModel):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(default=0)
    comment = models.TextField()
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.business.name}"

class Favorite(BaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)

class Report(BaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    reason = models.TextField()
