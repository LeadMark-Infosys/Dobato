from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
import secrets

from .models import (
    PageMeta,
    PageVersion,
    PageSection,
    PageMedia,
    Page,
    PagePreviewToken,
    PageSlugHistory,
)
from .serializers import (
    PageVersionSerializer,
    PageMetaSerializer,
    PageSectionSerializer,
    PageMediaSerializer,
    PageSerializer,
    PageListSerializer,
    PagePreviewTokenSerializer,
)
from apps.core.views import MunicipalityTenantModelViewSet
from apps.core.permissions import IsDataEntryOrDataManagerAndApproved


class PublicPageView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(60 * 5))
    def get(self, request, slug, language_code="en"):
        municipality = getattr(request, "tenant", None)
        try:
            page = Page.objects.get(
                municipality=municipality,
                slug=slug,
                language_code=language_code,
                status="published",
                is_deleted=False,
            )
        except Page.DoesNotExist:
            # check slug history
            hist = (
                PageSlugHistory.objects.filter(old_slug=slug)
                .order_by("-changed_at")
                .first()
            )
            if hist:
                return Response(
                    {"redirect": hist.new_slug},
                    status=301,
                )
            return Response({"detail": "Not found"}, status=404)
        ser = PageSerializer(page)
        return Response(ser.data)


class PreviewPageView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        try:
            t = PagePreviewToken.objects.select_related("page").get(token=token)
        except PagePreviewToken.DoesNotExist:
            return Response({"detail": "Invalid"}, status=404)
        if not t.is_valid():
            return Response({"detail": "Expired"}, status=410)
        ser = PageSerializer(t.page)
        return Response(ser.data)


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
        return queryset.filter(is_deleted=False, municipality=self.request.tenant)

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

    def _unique_slug_copy(self, slug, municipality, language_code):
        candidate = f"{slug}-copy"
        idx = 2
        while Page.objects.filter(
            municipality=municipality,
            slug=candidate,
            language_code=language_code,
            is_deleted=False,
        ).exists():
            candidate = f"{slug}-copy-{idx}"
            idx += 1
        return candidate

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
        new_slug = self._unique_slug_copy(
            original_page.slug, original_page.municipality, original_page.language_code
        )

        duplicate_page = Page.objects.create(
            municipality=original_page.municipality,
            title=f"{original_page.title} (Copy)",
            slug=new_slug,
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
        except PageVersion.DoesNotExist:
            return Response(
                {"error": "Version not found"}, status=status.HTTP_404_NOT_FOUND
            )
        snapshot = version.snapshot or {}
        with transaction.atomic():
            for field in ["title", "body", "banner_image", "template", "status"]:
                if field in snapshot:
                    setattr(page, field, snapshot[field])
            # slug rollback (optional) - ensure uniqueness
            if "slug" in snapshot and snapshot["slug"] != page.slug:
                candidate = snapshot["slug"]
                i = 2
                while (
                    Page.objects.filter(
                        municipality=page.municipality,
                        slug=candidate,
                        language_code=page.language_code,
                        is_deleted=False,
                    )
                    .exclude(id=page.id)
                    .exists()
                ):
                    candidate = f"{snapshot['slug']}-{i}"
                    i += 1
                page.slug = candidate
            page.updated_by = request.user
            page.save()
            meta_data = snapshot.get("meta")
            if meta_data:
                from .models import PageMeta

                meta, _ = PageMeta.objects.update_or_create(page=page)
                for k, v in meta_data.items():
                    setattr(meta, k, v)
                meta.save()
            sections = snapshot.get("sections", [])
            if sections:
                page.sections.all().delete()
                for s in sections:
                    PageSection.objects.create(
                        page=page,
                        title=s["title"],
                        content=s["content"],
                        type=s["type"],
                        position=s["position"],
                        is_active=s["is_active"],
                    )
            media_items = snapshot.get("media", [])
            if media_items:
                page.media.all().delete()
                for m in media_items:
                    PageMedia.objects.create(
                        page=page,
                        media_url=m["media_url"],
                        caption=m["caption"],
                        is_featured=m["is_featured"],
                    )
        return Response({"detail": "Rolled back."})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def create_preview_token(self, request, pk=None):
        page = self.get_object()
        ttl_minutes = int(request.data.get("ttl_minutes", 30))
        token = secrets.token_urlsafe(32)
        expires = timezone.now() + timezone.timedelta(minutes=ttl_minutes)
        preview = PagePreviewToken.objects.create(
            page=page, token=token, expires_at=expires, created_by=request.user
        )
        return Response(PagePreviewTokenSerializer(preview).data, status=201)


class PageMetaViewSet(viewsets.ModelViewSet):
    queryset = PageMeta.objects.all()
    serializer_class = PageMetaSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]

    def get_queryset(self):
        return PageMeta.objects.filter(page__municipality=self.request.tenant)


class PageVersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PageVersion.objects.all()
    serializer_class = PageVersionSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]

    def get_queryset(self):
        return PageVersion.objects.filter(page__municipality=self.request.tenant)


class PageSectionViewSet(viewsets.ModelViewSet):
    queryset = PageSection.objects.all()
    serializer_class = PageSectionSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]
    ordering = ["position"]

    def get_queryset(self):
        return PageSection.objects.filter(page__municipality=self.request.tenant)


class PageMediaViewSet(viewsets.ModelViewSet):
    queryset = PageMedia.objects.all()
    serializer_class = PageMediaSerializer
    permission_classes = [IsDataEntryOrDataManagerAndApproved]

    def get_queryset(self):
        return PageMedia.objects.filter(page__municipality=self.request.tenant)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def set_featured(self, request, pk=None):
        media = self.get_object()
        PageMedia.objects.filter(page=media.page).update(is_featured=False)
        media.is_featured = True
        media.save()
        return Response({"detail": "Media set as featured."}, status=status.HTTP_200_OK)
