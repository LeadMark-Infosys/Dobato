from django.utils import timezone

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *

from apps.core.views import MunicipalityTenantModelViewSet
from apps.core.permissions import IsDataEntryOrDataManagerAndApproved

class FeedbackViewSet(MunicipalityTenantModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        super().perform_create(serializer, submitted_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsDataEntryOrDataManagerAndApproved])
    def approve(self, request, pk=None):
        feedback = self.get_object()

        if feedback.is_approved:
            return Response(
                {'detail': 'This feedback has already been approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update feedback fields
        feedback.is_approved = True
        feedback.approved_by = request.user
        feedback.approved_at = timezone.now()
        feedback.save()

        serializer = self.get_serializer(feedback)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MediaViewSet(ModelViewSet):
    queryset = FeedbackMedia.objects.all()
    serializer_class = FeedbackMediaSerializer
    permission_classes = [IsAuthenticated]

