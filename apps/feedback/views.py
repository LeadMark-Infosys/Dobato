from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated

class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        
        serializer.save(submitted_by=self.request.user)


class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

class FeedbackCategoryViewSet(ModelViewSet):
    queryset = FeedbackCategory.objects.all()
    serializer_class = FeedbackCategorySerializer

class QRLocationViewSet(ModelViewSet):
    queryset = QRLocation.objects.all()
    serializer_class = QRLocationSerializer

class FeedbackStatusViewSet(ModelViewSet):
    queryset = FeedbackStatus.objects.all()
    serializer_class = FeedbackStatusSerializer

class FeedbackResponseViewSet(ModelViewSet):
    queryset = FeedbackResponse.objects.all()
    serializer_class = FeedbackResponseSerializer

class AttachmentViewSet(ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer

