from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet, ReviewViewSet, FavoriteViewSet

router = DefaultRouter()
router.register(r'', BusinessViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'favorites', FavoriteViewSet)  

urlpatterns = [
    path('', include(router.urls)),
]
