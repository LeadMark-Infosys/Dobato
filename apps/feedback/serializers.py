from rest_framework import serializers
from .models import Feedback, FeedbackCategory, QRLocation, FeedbackStatus

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

    def validate_approved_by(self, value):
        if value and value.user_type != 'municipality_admin':
            raise serializers.ValidationError("Only municipality_admin can approve feedback.")
        return value

class FeedbackCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackCategory
        fields = '__all__'

class QRLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRLocation
        fields = '__all__'

class FeedbackStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackStatus
        fields = '__all__'

class FeedbackResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

    def validate_responder(self, value):
        if value and value.user_type != 'municipality_admin':
            raise serializers.ValidationError("Only municipality_admin can respond to feedback.")
        return value

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['qr_code_image']  
        read_only_fields = ['qr_code_image']