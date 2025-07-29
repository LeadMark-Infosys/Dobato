from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TouristPlaceViewSet, StorySectionViewSet, ReviewViewSet, MediaViewSet

router = DefaultRouter()
router.register(r'places', TouristPlaceViewSet)
router.register(r'stories', StorySectionViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'media', MediaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
