import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone
from apps.municipality.models import MunicipalityAwareModel
from apps.core.models import BaseModel
from django.forms.models import model_to_dict

class PageSlugHistory(models.Model):
    page = models.ForeignKey(
        "Page", on_delete=models.CASCADE, related_name="slug_history"
    )
    old_slug = models.SlugField(max_length=255)
    new_slug = models.SlugField(max_length=255)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["old_slug", "page", "changed_at"])]

    def __str__(self):
        return f"{self.old_slug} -> {self.new_slug}"


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
        unique_together = (("municipality", "slug", "language_code"),)
        indexes = [
            models.Index(fields=["municipality", "slug", "language_code"]),
            models.Index(fields=["municipality", "status", "published_at"]),
            models.Index(fields=["municipality", "language_code"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.language_code}) - {self.municipality.name}"

    def _build_snapshot(self):
        meta = None
        if hasattr(self, "meta"):
            meta = model_to_dict(
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
                    "title": s.title,
                    "content": s.content,
                    "type": s.type,
                    "position": s.position,
                    "is_active": s.is_active,
                }
                for s in self.sections.order_by("position")
            ]
            media = [
                {
                    "media_url": m.media_url,
                    "caption": m.caption,
                    "is_featured": m.is_featured,
                }
                for m in self.media.all()
            ]
            return {
                "title": self.title,
                "body": self.body,
                "slug": self.slug,
                "meta": meta,
                "sections": sections,
                "media": media,
            }

    def create_version(self):
        snapshot = self._build_snapshot()
        last = self.version.order_by("-version_number").first()
        if last and last.snapshot == snapshot:
            return
        version_number = (last.version_number + 1) if last else 1
        PageVersion.objects.create(
            page=self,
            version_number=version_number,
            title=self.title,
            body=self.body,
            editor=self.updated_by,
            change_note=f"Auto-saved version {version_number}",
            snapshot=snapshot,
        )

        old_versions = self.versions.order_by("-version_number")[20:]
        if old_versions:
            PageVersion.objects.filter(id__in=[v.id for v in old_versions]).delete()

    def save(self, *args, **kwargs):
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
            PageSlugHistory.objects.create(
                page=self, old_slug=old_slug, new_slug=self.slug
            )
        if self.pk:
            self.create_version()

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

        if self.slug in self.RESERVED_SLUGS:
            raise ValidationError("Slug is reserved.")


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
        unique_together = (("page", "version_number"),)
        ordering = ["-version_number"]
        indexes = [
            models.Index(fields=["page", "version_number"]),
        ]

    def __str__(self):
        return f"{self.page.title} - Version {self.version_number} - {self.page.municipality.name}"

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
    media_url = models.TextField()
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="media")
    caption = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False)
    def __str__(self):
        return f"Media for {self.page.title} - {self.page.municipality.name}"
