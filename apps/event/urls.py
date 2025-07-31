from rest_framework import routers
from .views import (
    EventCategoryViewSet, EventLocationViewSet, EventViewSet,
    EventScheduleViewSet, OrganizerInfoViewSet, EventMediaViewSet,
    EventPublicInteractionViewSet, BookmarkViewSet
)
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'categories', EventCategoryViewSet)
router.register(r'locations', EventLocationViewSet)
router.register(r'events', EventViewSet)
router.register(r'schedules', EventScheduleViewSet)
router.register(r'organizers', OrganizerInfoViewSet)
router.register(r'media', EventMediaViewSet)
router.register(r'interactions', EventPublicInteractionViewSet)
router.register(r'bookmarks', BookmarkViewSet)


urlpatterns = [
    path('', include(router.urls)),
]