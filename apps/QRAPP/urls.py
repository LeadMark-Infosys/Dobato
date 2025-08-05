from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QRViewSet

router = DefaultRouter()
router.register(r'qrs', QRViewSet, basename='qr')

urlpatterns = [
    path('', include(router.urls)),
]
