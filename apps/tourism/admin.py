from django.contrib import admin
from .models import (TouristPlace, StorySection, Review, Media)

@admin.register(TouristPlace)
class TourismPlaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'approval_status']


@admin.register(StorySection)
class PlaceStoryAdmin(admin.ModelAdmin):
    list_display = ['place', 'short_description']

@admin.register(Review)
class PlaceReviewAdmin(admin.ModelAdmin):
    list_display = ['place', 'user_name', 'rating', 'is_approved']

@admin.register(Media)
class PlaceMediaAdmin(admin.ModelAdmin):
    list_display = ['place', 'vr_supported']
