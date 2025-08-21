from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    PageViewSet,
    PageMetaViewSet,
    PageSectionViewSet,
    PageMediaViewSet,
    PageVersionViewSet,
)

router = SimpleRouter()
router.register(r"pages", PageViewSet)
router.register(r"page-meta", PageMetaViewSet)
router.register(r"page-sections", PageSectionViewSet)
router.register(r"page-media", PageMediaViewSet)
router.register(r"page-versions", PageVersionViewSet)

urlpatterns = [path("", include(router.urls))]
