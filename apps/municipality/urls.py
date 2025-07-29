from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MunicipalityViewSet


router = DefaultRouter()
router.register(r'municipalities', MunicipalityViewSet)

urlpatterns = [
   path('', include(router.urls)),
]