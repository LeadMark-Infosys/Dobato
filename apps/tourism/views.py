from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from apps.core.views import MunicipalityTenantModelViewSet
from apps.core.permissions import IsDataEntryOrDataManagerAndApproved
from .models import *
from .serializers import *

class TouristPlaceViewSet(MunicipalityTenantModelViewSet):
    queryset = TouristPlace.objects.all()
    serializer_class = TouristPlaceSerializer
    permission_classes = [AllowAny]

class StorySectionViewSet(ModelViewSet):
    queryset = StorySection.objects.all()
    serializer_class = StorySectionSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]

class MediaViewSet(ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]

class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]