from rest_framework import viewsets
from .models import (
    EventCategory, EventLocation, Event, EventSchedule,
    OrganizerInfo, EventMedia, MultiLingualEvent
)
from .serializers import (
    EventCategorySerializer, EventLocationSerializer, EventSerializer,
    EventScheduleSerializer, OrganizerInfoSerializer, EventMediaSerializer,
    MultiLingualEventSerializer
)

class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer

class EventLocationViewSet(viewsets.ModelViewSet):
    queryset = EventLocation.objects.all()
    serializer_class = EventLocationSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class EventScheduleViewSet(viewsets.ModelViewSet):
    queryset = EventSchedule.objects.all()
    serializer_class = EventScheduleSerializer

class OrganizerInfoViewSet(viewsets.ModelViewSet):
    queryset = OrganizerInfo.objects.all()
    serializer_class = OrganizerInfoSerializer

class EventMediaViewSet(viewsets.ModelViewSet):
    queryset = EventMedia.objects.all()
    serializer_class = EventMediaSerializer

class MultiLingualEventViewSet(viewsets.ModelViewSet):
    queryset = MultiLingualEvent.objects.all()
    serializer_class = MultiLingualEventSerializer