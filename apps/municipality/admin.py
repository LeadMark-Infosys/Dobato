from django.contrib import admin

from .models import Municipality

@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'unique_slug', 'full_domain', 'primary_color', 'default_language', 'time_zone', 'is_active')