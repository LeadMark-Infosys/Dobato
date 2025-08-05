from rest_framework import serializers
from .models import (
    FeedbackCategory,
    FeedbackStatus,
    Feedback,
    FeedbackResponse,
    Attachment,
    QR
)
from django.contrib.auth import get_user_model

User = get_user_model()

class FeedbackCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackCategory
        fields = '__all__'

class FeedbackStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackStatus
        fields = '__all__'

class FeedbackResponseSerializer(serializers.ModelSerializer):
    responder = serializers.StringRelatedField()

    class Meta:
        model = FeedbackResponse
        exclude = ['feedback']

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']

class FeedbackSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Feedback
        fields = '__all__'

class QRSerializer(serializers.ModelSerializer):
    class Meta:
        model = QR
        fields = '__all__'
