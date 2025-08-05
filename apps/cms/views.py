from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import action
from django.utils import timezone

from .models import PageMeta, PageVersion, PageSection, PageMedia
from .serializers import (
    PageVersionSerializer,
)
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

    def destroy(self, request, *args, **kwargs):
        page = self.get_object()
        page.is_deleted = True
        page.updated_by = request.user
        page.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def publish(self, request, pk=None):
        page = self.get_object()
        if page.status != "published":
            page.status = "published"
            page.published_at = timezone.now()
            page.updated_by = request.user
            page.save()
            return Response(
                {"detail": "Page published successfully."}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "Page is already published."}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def unpublish(self, request, pk=None):
        page = self.get_object()
        if page.status == "published":
            page.status = "draft"
            page.unpublished_at = timezone.now()
            page.updated_by = request.user
            page.save()
            return Response(
                {"detail": "Page unpublished successfully."}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "Page is not published."}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        original_page = self.get_object()

        duplicate_page = Page.objects.create(
            municipality=original_page.municipality,
            title=f"{original_page.title} (Copy)",
            slug=f"{original_page.slug}-copy",
            language_code=original_page.language_code,
            body=original_page.body,
            banner_image=original_page.banner_image,
            template=original_page.template,
            status="draft",
            created_by=request.user,
            updated_by=request.user,
        )

        if hasattr(original_page, "meta"):
            PageMeta.objects.create(
                page=duplicate_page,
                meta_title=original_page.meta.meta_title,
                meta_description=original_page.meta.meta_description,
                canonical_url=original_page.meta.canonical_url,
                og_title=original_page.meta.og_title,
                og_description=original_page.meta.og_description,
                og_image=original_page.meta.og_image,
                robots_directive=original_page.meta.robots_directive,
            )

        for section in original_page.sections.all():
            PageSection.objects.create(
                page=duplicate_page,
                title=section.title,
                content=section.content,
                type=section.type,
                position=section.position,
                is_active=section.is_active,
            )

        for media in original_page.media.all():
            PageMedia.objects.create(
                page=duplicate_page,
                media_url=media.media_url,
                caption=media.caption,
                is_featured=media.is_featured,
            )

        serializer = self.get_serializer(duplicate_page)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):
        page = self.get_object()
        versions = page.versions.all()
        serializer = PageVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(
        detail=True, methods=["post"], url_path="rollback/(?P<version_number>[^/.]+)"
    )
    def rollback(self, request, pk=None, version_number=None):
        page = self.get_object()
        try:
            version = page.versions.get(version_number=version_number)
            page.title = version.title
            page.body = version.body
            page.updated_by = request.user
            page.save()
            return Response({"detail": f"Rolled back to version {version_number}"})
        except PageVersion.DoesNotExist:
            return Response(
                {"error": "Version not found"}, status=status.HTTP_404_NOT_FOUND
            )
