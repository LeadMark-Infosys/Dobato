import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from .manager import CustomUserManager
from apps.core.models import BaseModel
from apps.municipality.models import Municipality



class AdminUser(AbstractBaseUser):
    USER_TYPE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('support_user', 'support_user'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=255)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'

    def __str__(self):
        return f"{self.email} ({self.role})"


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    USER_TYPE_CHOICES = [
        ('public', 'Public User'),
        ('municipality_admin', 'Municipality Admin'),
        ('department_manager', 'Department Manager'),
        ('data_entry_user', 'Data Entry User'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=200, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=255)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='public')
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
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
