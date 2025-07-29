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
