from rest_framework import serializers
from .models import (
    Feedback,
    FeedbackCategory,
    QRLocation,
    FeedbackStatus,
    FeedbackResponse,
    Attachment,
    QRAnalytics
)
class FeedbackCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackCategory
        fields = '__all__'

class FeedbackStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackStatus
        fields = '__all__'

class QRLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRLocation
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
    def validate_approved_by(self, value):
        if value and value.user_type != 'municipality_admin':
            raise serializers.ValidationError("Only municipality_admin can approve feedback.")
        return value

class FeedbackResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackResponse
        fields = '__all__'
    def validate_responder(self, value):
        if value and value.user_type not in ['municipality_admin', 'department_manager']:
            raise serializers.ValidationError("Only municipality_admin or department_manager can respond to feedback.")
        return value

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'

class QRAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRAnalytics
        fields = '__all__'
