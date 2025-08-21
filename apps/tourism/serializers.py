from rest_framework import serializers
from .models import (
    TouristPlace,
    StorySection,
    Media,
    Review,

)
class TouristPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TouristPlace
        fields = '__all__'
        read_only_fields = ['municipality', 'version', 'last_edited']

    def validate(self, data):
        municipality = data.get("municipality") or getattr(self.instance, "municipality", None)
        if municipality and not municipality.is_active:
            raise serializers.ValidationError(
                {"municipality": "Cannot add tourist place because the municipality is inactive."}
            )
        return data
class StorySectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorySection
        fields = '__all__'

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
