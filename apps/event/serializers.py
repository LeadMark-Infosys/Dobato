from rest_framework import serializers
from .models import (
    EventCategory, EventLocation, Event, EventSchedule,
    OrganizerInfo, EventMedia, EventPublicInteraction,Bookmark
)

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'

class EventLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLocation
        fields = '__all__'
        
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

    def validate(self, data):
        municipality = data.get("municipality") or getattr(self.instance, "municipality", None)
        if municipality and not municipality.is_active:
            raise serializers.ValidationError(
                {"municipality": "Cannot add event because the municipality is inactive."}
            )
        return data


class EventScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSchedule
        fields = '__all__'

class OrganizerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizerInfo
        fields = '__all__'

class EventMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventMedia
        fields = '__all__'

class EventPublicInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPublicInteraction
        fields = '__all__'

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = '__all__'