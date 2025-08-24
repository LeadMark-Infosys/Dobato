import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone
from apps.municipality.models import MunicipalityAwareModel
from apps.core.models import BaseModel
from django.db.models import Q
from django.forms.models import model_to_dict
from urllib.parse import urlparse

VERSION_TRACKED_FIELDS = getattr(
    settings,
    "CMS_VERSION_TRACKED_FIELDS",
    ["title", "slug", "body", "banner_image", "template", "status", "language_code"],
)

CONTENT_SNAPSHOT_FIELDS = VERSION_TRACKED_FIELDS


class PageSlugHistory(models.Model):
    page = models.ForeignKey(
        "Page", on_delete=models.CASCADE, related_name="slug_history"
    )
    old_slug = models.SlugField(max_length=255)
    new_slug = models.SlugField(max_length=255)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["old_slug", "page"]),
            models.Index(fields=["new_slug", "page", "changed_at"]),
        ]
        ordering = ["-changed_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["old_slug", "page"], name="unique_old_slug_page"
            )
        ]

    def __str__(self):
        return f"{self.old_slug} -> {self.new_slug}"


class PagePreviewToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(
        "Page", on_delete=models.CASCADE, related_name="preview_tokens"
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def is_valid(self):
        return timezone.now() < self.expires_at


class Page(MunicipalityAwareModel, BaseModel):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending", "Pending Review"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    TEMPLATE_CHOICES = [
        ("default", "Default"),
        ("landing", "Landing Page"),
        ("article", "Article"),
        ("contact", "Contact"),
        ("about", "About"),
    ]

    RESERVED_SLUGS = {"admin", "api", "static", "media", "sitemap", "robots", "assets"}

    scheduled_publish_at = models.DateTimeField(null=True, blank=True)
    scheduled_unpublish_at = models.DateTimeField(null=True, blank=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    language_code = models.CharField(max_length=10, default="en")
    body = models.TextField(blank=True)
    banner_image = models.TextField(blank=True)
    template = models.CharField(
        max_length=100, choices=TEMPLATE_CHOICES, default="default"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    unpublished_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    translated_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="translations",
    )

    class Meta:
        indexes = [
            models.Index(fields=["municipality", "slug", "language_code"]),
            models.Index(fields=["municipality", "status", "published_at"]),
            models.Index(fields=["municipality", "language_code"]),
            models.Index(fields=["municipality", "scheduled_publish_at"]),
            models.Index(fields=["municipality", "scheduled_unpublish_at"]),
            models.Index(fields=["municipality", "is_featured"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["municipality", "slug", "language_code"],
                condition=Q(is_deleted=False),
                name="unique_page_slug_active",
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.language_code}) - {self.municipality.name}"

    def _reserved_slugs(self):
        return getattr(settings, "CMS_RESERVED_SLUGS", self.RESERVED_SLUGS)

    def clean(self):
        if (
            Page.objects.filter(
                municipality=self.municipality,
                slug=self.slug,
                language_code=self.language_code,
                is_deleted=False,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("Slug must be unique per municipality and language.")

        if self.slug in self._reserved_slugs():
            raise ValidationError({"slug": "This Slug is reserved."})

    def _build_snapshot(self):
        meta_dict = None
        if hasattr(self, "meta"):
            meta_dict = model_to_dict(
                self.meta,
                fields=[
                    "meta_title",
                    "meta_description",
                    "canonical_url",
                    "og_title",
                    "og_description",
                    "og_image",
                    "robots_directive",
                ],
            )
            sections = [
                {
                    "id": str(s.id),
                    "title": s.title,
                    "content": s.content,
                    "type": s.type,
                    "position": s.position,
                    "is_active": s.is_active,
                }
                for s in self.sections.order_by("position")
            ]
            media_items = [
                {
                    "id": str(m.id),
                    "media_url": m.media_url,
                    "caption": m.caption,
                    "is_featured": m.is_featured,
                }
                for m in self.media.all()
            ]
            data = {
                "meta": meta_dict,
                "sections": sections,
                "media": media_items,
            }
            for f in CONTENT_SNAPSHOT_FIELDS:
                data[f] = getattr(self, f, None)
            return data

    def _content_changed(self, snapshot):
        last = self.versions.order_by("-version_number").first()
        if not last:
            return True
        return last.snapshot != snapshot

    def create_version(self, change_note=None, user=None, force=False):
        snapshot = self._build_snapshot()
        last = self.versions.order_by("-version_number").first()
        if not force:
            if last and not self._content_changed(snapshot):
                return
            min_interval = getattr(settings, "CMS_VERSION_MIN_INTERVAL_SECONDS", 0)
            if last and min_interval:
                if (timezone.now() - last.created_at).total_seconds() < min_interval:
                    return
        next_number = 1 if not last else last.version_number + 1

        PageVersion.objects.create(
            page=self,
            version_number=next_number,
            title=self.title,
            body=self.body,
            editor=user or getattr(self, "updated_by", None),
            change_note=change_note or f"Auto version {next_number}",
            snapshot=snapshot,
        )

        max_versions = getattr(settings, "CMS_MAX_PAGE_VERSIONS", 20)
        stale = self.versions.order_by("-created_at")[max_versions:]
        if stale:
            PageVersion.objects.filter(id__in=[v.id for v in stale]).delete()

    def save(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        old_slug = None
        if self.pk:
            try:
                old_slug = Page.objects.get(pk=self.pk).slug
            except Page.DoesNotExist:
                pass
        if not self.slug:
            self.slug = slugify(self.title)
        if self.slug in self.RESERVED_SLUGS:
            raise ValidationError("Slug is reserved.")
        if self.status == "published" and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
        if old_slug and old_slug != self.slug:
            if not PageSlugHistory.objects.filter(
                page=self, old_slug=old_slug
            ).exists():
                PageSlugHistory.objects.create(
                    page=self, old_slug=old_slug, new_slug=self.slug
                )
        try:
            self.create_version(user=user)
        except Exception:
            pass


class PageMeta(models.Model):
    page = models.OneToOneField(Page, on_delete=models.CASCADE, related_name="meta")
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    canonical_url = models.URLField(blank=True)
    og_title = models.CharField(max_length=255, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.TextField(blank=True)
    robots_directive = models.CharField(
        max_length=50, blank=True, default="index, follow"
    )

    def clean(self):
        enforce_https = getattr(settings, "CMS_ENFORCE_HTTPS_CANONICAL", True)
        if self.canonical_url:
            parsed = urlparse(self.canonical_url)
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError(
                    {"canonical_url": "Canonical URL must be absolute ."}
                )
            if parsed.scheme not in ("http", "https"):
                raise ValidationError(
                    {"canonical_url": "Canonical URL must be HTTP or HTTPS."}
                )
            if enforce_https and parsed.scheme != "https":
                raise ValidationError({"canonical_url": "Canonical URL must be HTTPS."})

    def __str__(self):
        return f"Meta for {self.page.title} - {self.page.municipality.name}"


class PageVersion(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    snapshot = models.JSONField(default=dict, blank=True)
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    change_note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-version_number"]
        indexes = [
            models.Index(fields=["page", "version_number"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["page", "version_number"],
                condition=Q(is_deleted=False),
                name="unique_page_version_active",
            )
        ]

    def __str__(self):
        return f"{self.page.title} - Version {self.versions_number} - {self.page.municipality.name}"


class PageSection(models.Model):
    SECTION_TYPES = [
        ("text", "Text"),
        ("image", "Image"),
        ("video", "Video"),
        ("cta", "Call to Action"),
        ("gallery", "Gallery"),
        ("embed", "Embed"),
        ("contact_form", "Contact Form"),
    ]

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(max_length=50, choices=SECTION_TYPES, default="text")
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["position"]
        indexes = [
            models.Index(fields=["page", "position"]),
        ]

    def __str__(self):
        return f"{self.page.title} - {self.title} - {self.page.municipality.name}"


class PageMedia(models.Model):
    media_url = models.TextField(blank=True)
    url = models.URLField(blank=True)
    file = models.ImageField(upload_to="page_media/", blank=True, null=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="media")
    caption = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["page", "is_featured"]),
            models.Index(fields=["is_featured"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=(Q(file__isnull=False) | ~Q(url="") | ~Q(media_url="")),
                name="page_media_requires_one_source",
            )
        ]

    def clean(self):
        if not (
            self.file or self.url.strip() or (self.media_url and self.media_url.strip())
        ):
            raise ValidationError("Provide a file or a URL.")

        if self.file and self.file.size > 5 * 1024 * 1024:
            raise ValidationError("File size should not exceed 5MB.")

    def __str__(self):
        return f"Media for {self.page.title} - {self.page.municipality.name}"
