from rest_framework.viewsets import ModelViewSet

from apps.core.views import MunicipalityTenantModelViewSet
from .models import *
from .serializers import *

class TouristPlaceViewSet(MunicipalityTenantModelViewSet):
    queryset = TouristPlace.objects.all()
    serializer_class = TouristPlaceSerializer

class StorySectionViewSet(ModelViewSet):
    queryset = StorySection.objects.all()
    serializer_class = StorySectionSerializer

class MediaViewSet(ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

