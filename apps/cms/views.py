from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.core.views import MunicipalityTenantModelViewSet
from apps.core.permissions import IsDataEntryOrDataManagerAndApproved
from .models import Page
from .serializers import PageSerializer, PageListSerializer


class PageViewSet(MunicipalityTenantModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "language_code", "is_featured", "template"]
    search_fields = ["title", "body"]
    ordering_fields = ["created_at", "updated_at", "published_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return PageListSerializer
        return PageSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(
            municipality=self.request.tenant,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
