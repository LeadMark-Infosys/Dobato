from rest_framework.serializers import (
    ModelSerializer, HiddenField, CurrentUserDefault
)
from django.contrib.auth import get_user_model
from .models import (
    Business, BusinessMedia, Review, Favorite,
    Report
)
from rest_framework import serializers

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

    def validate(self, data):
        municipality = data.get("municipality") or getattr(self.instance, "municipality", None)
        if municipality and not municipality.is_active:
            raise serializers.ValidationError(
                {"municipality": "Cannot add business because the municipality is inactive."}
            )
        return data

class BusinessMediaSerializer(ModelSerializer):
    class Meta:
        model = BusinessMedia
        fields = '__all__'

class ReviewSerializer(ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class FavoriteSerializer(ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())
    class Meta:
        model = Favorite
        fields = '__all__'

class ReportSerializer(ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'