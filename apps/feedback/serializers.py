from rest_framework import serializers
from .models import Feedback, FeedbackMedia

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
    def validate_approved_by(self, value):
        if value and value.user_type != 'municipality_admin':
            raise serializers.ValidationError("Only municipality_admin can approve feedback.")
        return value

class FeedbackMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackMedia
        fields = '__all__'
