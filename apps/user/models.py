import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from .manager import CustomUserManager
from apps.core.models import BaseModel

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    USER_TYPE_CHOICES = [
        ('traveler', 'Traveler'),
        ('company', 'Travel Company'),
        ('hotel_owner', 'Hotel Owner'),
        ('guide', 'Guide'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('seo', 'SEO Team'),
        ('content', 'Content Writer'),
        ('support', 'Support Agent'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=200, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=255)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='traveler')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']
    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
class UserOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.phone} - OTP: {self.otp}"

class UserProfile(models.Model):
    STATUS_CHOICES = [('married', 'Married'), ('unmarried', 'Unmarried')]
    USER_TYPE_CHOICES = [('customer', 'Customer'), ('guide', 'Guide'), ('hotel', 'Hotel')]
    PROFILE_TYPE_CHOICES = [('guest', 'Guest'), ('basic', 'Basic'), ('verified', 'Verified')]
    KYC_STATUS_CHOICES = [('approved', 'Approved'), ('pending', 'Pending'), ('rejected', 'Rejected')]
    PAYMENT_TYPE_CHOICES = [('fonepay', 'FonePay'), ('card', 'Card'), ('wallet', 'Wallet'), ('cash', 'Cash')]
    PRICE_SENSITIVITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    address = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=20, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='married')
    dob = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.TextField(blank=True, null=True)
    preferred_pronouns = models.CharField(max_length=50, blank=True, null=True)
    theme = models.CharField(max_length=50, choices=[('light', 'Light'), ('dark', 'Dark')], default='light', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    preferred_currency = models.CharField(max_length=10, blank=True, null=True)
    preferred_timezone = models.CharField(max_length=50, blank=True, null=True)
    passport_country = models.CharField(max_length=100, blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    profile_type = models.CharField(max_length=20, choices=PROFILE_TYPE_CHOICES, default='guest')
    id_card_number = models.CharField(max_length=20, blank=True, null=True)
    kyc_status = models.CharField(max_length=20, choices=KYC_STATUS_CHOICES, default='pending')
    emergency_contact = models.CharField(max_length=30, blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True)
    preferred_payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='fonepay')
    budget_range = models.CharField(max_length=50, blank=True, null=True)
    price_sensitivity_level = models.CharField(max_length=10, choices=PRICE_SENSITIVITY_CHOICES, default='medium')
    
    def __str__(self):
        return f"{self.user.name}'s Profile"