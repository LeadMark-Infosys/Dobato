import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from .manager import CustomUserManager
from apps.core.models import BaseModel
from apps.municipality.models import Municipality

#class tenantuser
# super admin, support user
# apps/users/models.py
class TenantUser(BaseModel):
    class Roles(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        SUPPORT_USER = "support_user", "Support User"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=30, choices=Roles.choices)
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'

    def __str__(self):
        return f"{self.email} ({self.role})"

class Roles(models.TextChoices):
    MUNICIPALITY_ADMIN = "municipality_admin", "Municipality Admin"
    DEPARTMENT_MANAGER = "department_manager", "Department Manager"
    STAFF = "data_entry_user", "Data Entry User"
    PUBLIC = "public", "Public User"

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
   
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=200, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=30, choices=Roles.choices, default=Roles.PUBLIC)
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
