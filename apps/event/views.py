from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from apps.core.permissions import IsDataEntryOrDataManagerAndApproved
from .models import (
    EventCategory, EventLocation, Event, EventSchedule,
    OrganizerInfo, EventMedia, EventPublicInteraction,Bookmark
)
from apps.core.views import MunicipalityTenantModelViewSet
from .serializers import (
    EventCategorySerializer, EventLocationSerializer, EventSerializer,
    EventScheduleSerializer, OrganizerInfoSerializer, EventMediaSerializer,
    EventPublicInteractionSerializer, BookmarkSerializer
)

class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer
    permission_classes = [AllowAny]

class EventLocationViewSet(viewsets.ModelViewSet):
    queryset = EventLocation.objects.all()
    serializer_class = EventLocationSerializer
    permission_classes = [AllowAny]

class EventViewSet(MunicipalityTenantModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]  # Adjust permissions as needed

class EventScheduleViewSet(viewsets.ModelViewSet):
    queryset = EventSchedule.objects.all()
    serializer_class = EventScheduleSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]

class OrganizerInfoViewSet(viewsets.ModelViewSet):
    queryset = OrganizerInfo.objects.all()
    serializer_class = OrganizerInfoSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]

class EventMediaViewSet(viewsets.ModelViewSet):
    queryset = EventMedia.objects.all()
    serializer_class = EventMediaSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]

class EventPublicInteractionViewSet(viewsets.ModelViewSet):
    queryset = EventPublicInteraction.objects.all()
    serializer_class = EventPublicInteractionSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]

class BookmarkViewSet(viewsets.ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]