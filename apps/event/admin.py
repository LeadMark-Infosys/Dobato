from django.contrib import admin
from .models import (
    EventCategory, EventLocation, Event, EventSchedule,
    OrganizerInfo, EventMedia, MultiLingualEvent
)
@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(EventLocation)
class EventLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'latitude', 'longitude')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'category', 'registration_type', 'ticket_price')

@admin.register(EventSchedule)
class EventScheduleAdmin(admin.ModelAdmin):
    list_display = ('event', 'start_time', 'end_time', 'category', 'Max_attendees')

@admin.register(OrganizerInfo)
class OrganizerInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'event')

@admin.register(EventMedia)
class EventMediaAdmin(admin.ModelAdmin):
    list_display = ('event', 'media_url')
@admin.register(MultiLingualEvent)
class MultiLingualEventAdmin(admin.ModelAdmin):
    list_display = ('event', 'language_code', 'title')