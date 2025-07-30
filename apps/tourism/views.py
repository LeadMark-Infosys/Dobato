from rest_framework.viewsets import ModelViewSet

from apps.core.views import MunicipalityTenantModelViewSet
from .permissions import IsDataEntryOrDataManagerAndApproved
from .models import *
from .serializers import *

class TouristPlaceViewSet(MunicipalityTenantModelViewSet):
    queryset = TouristPlace.objects.all()
    serializer_class = TouristPlaceSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]

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