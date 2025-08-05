from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    FeedbackCategory,
    FeedbackStatus,
    Feedback,
    FeedbackResponse,
    Attachment,
    QR
)

from .serializers import (
    FeedbackCategorySerializer,
    FeedbackStatusSerializer,
    FeedbackSerializer,
    FeedbackResponseSerializer,
    AttachmentSerializer,
    QRSerializer
)


class FeedbackCategoryViewSet(ModelViewSet):
    queryset = FeedbackCategory.objects.all()
    serializer_class = FeedbackCategorySerializer

class FeedbackStatusViewSet(ModelViewSet):
    queryset = FeedbackStatus.objects.all()
    serializer_class = FeedbackStatusSerializer

class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['submitted_at', 'approved_at']
    filterset_fields = ['status', 'category']

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user, municipality=self.request.user.municipality)

class FeedbackResponseViewSet( ModelViewSet):
    queryset = FeedbackResponse.objects.all()
    serializer_class = FeedbackResponseSerializer
    permission_classes = [IsAuthenticated]

class AttachmentViewSet(ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]

class QRViewSet(ModelViewSet):
    queryset = QR.objects.all()
    serializer_class = QRSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['total_scans', 'last_scanned']
    filterset_fields = ['entity_type']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, municipality=self.request.user.municipality)
