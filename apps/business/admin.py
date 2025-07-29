from django.contrib import admin
from .models import (
    Business, Review, Favorite, Report,
    BusinessMedia,

)

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'reg_no', 'address', 'pricing_type', 'authorized_person')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'rating', 'approved', 'comment', 'created_at', 'updated_at')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'created_at')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'reason', 'created_at', 'updated_at')

@admin.register(BusinessMedia)
class BusinessMediaAdmin(admin.ModelAdmin):
    list_display = ('business', 'media_url')
