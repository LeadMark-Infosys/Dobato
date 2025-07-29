from django.db import models

from apps.core.models import BaseModel

class Municipality(models.Model):

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('np', 'Nepali'),
    ]    

    name = models.CharField(max_length=100, unique=True)
    unique_slug = models.SlugField(max_length=100, unique=True)
    full_domain = models.CharField(max_length=255, unique=True)
    logo = models.CharField(max_length=255, blank=True, null=True)
    primary_color = models.CharField(max_length=20, blank=True, null=True)
    default_language = models.CharField(max_length=10, choices = LANGUAGE_CHOICES, default='en')
    time_zone = models.CharField(max_length=50, default='Asia/Kathmandu')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class MunicipalityAwareModel(models.Model):
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name='%(class)s_related',blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} - {self.municipality.name}"
    
