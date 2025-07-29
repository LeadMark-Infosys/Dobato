from rest_framework.serializers import (
    ModelSerializer, HiddenField, CurrentUserDefault
)
from django.contrib.auth import get_user_model
from .models import (
    Business, BusinessMedia, Review, Favorite,
    Report
)

class BusinessSerializer(ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

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