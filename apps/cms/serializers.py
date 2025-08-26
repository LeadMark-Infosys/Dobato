from rest_framework import serializers
from django.db import transaction
from urllib.parse import urlparse
from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import (
    PageMeta,
    PageVersion,
    PageSection,
    PageMedia,
    Page,
    PagePreviewToken,
)
import bleach

ALLOWED_TAGS = [
    "p",
    "br",
    "span",
    "div",
    "img",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "a",
    "strong",
    "em",
    "blockquote",
    "code",
    "pre",
]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel", "target"],
    "img": ["src", "alt", "title", "width", "height"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def clean_html(value: str) -> str:
    return bleach.clean(
        value or "",
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def sanitize_section_content(value):
    return clean_html(value)


def sanitize_meta_text(value: str) -> str:
    return bleach.clean(
        value or "", tags=[], attributes={}, protocols=ALLOWED_PROTOCOLS, strip=True
    )


class PageMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageMeta
        fields = [
            "meta_title",
            "meta_description",
            "canonical_url",
            "og_title",
            "og_description",
            "og_image",
            "robots_directive",
        ]

    def validate_canonical_url(self, v):
        if not v:
            return v
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise serializers.ValidationError(
                "Canonical URL must be absolute (include scheme and host)."
            )
        if parsed.scheme not in ("http", "https"):
            raise serializers.ValidationError("Canonical URL must be HTTP or HTTPS.")
        if (
            getattr(settings, "CMS_ENFORCE_HTTPS_CANONICAL", True)
            and parsed.scheme != "https"
        ):
            raise serializers.ValidationError("Canonical URL must be HTTPS.")
        return v

    def validate(self, attrs):
        for key in [
            "meta_title",
            "meta_description",
            "og_title",
            "og_description",
            "og_image",
            "robots_directive",
        ]:
            if key in attrs:
                attrs[key] = sanitize_meta_text(attrs[key])
        return attrs


class PageSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageSection
        fields = ["id", "title", "content", "type", "position", "is_active"]
        read_only_fields = ["id"]

    def validate_content(self, v):
        return sanitize_section_content(v)


class PageMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageMedia
        fields = ["id", "media_url", "url", "file", "caption", "is_featured"]
        read_only_fields = ["id"]

    def validate_url(self, v):
        if not v:
            return v
        validator = URLValidator(schemes=["http", "https"])
        try:
            validator(v)
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid URL format.")
        return v

    def validate_media_url(self, v):
        if not v:
            return v
        validator = URLValidator(schemes=["http", "https"])
        try:
            validator(v)
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid media URL .")
        return v

    def validate(self, attrs):
        url = attrs.get("url") or getattr(self.instance, "url", "")
        media_url = attrs.get("media_url") or getattr(self.instance, "media_url", "")
        file = attrs.get("file") or getattr(self.instance, "file", None)
        if not (file or (url and url.strip()) or (media_url and media_url.strip())):
            raise serializers.ValidationError(
                "Provide at least one of file, url, or media_url."
            )
        if "caption" in attrs:
            attrs["caption"] = sanitize_meta_text(attrs["caption"])
        return attrs


class PageVersionSerializer(serializers.ModelSerializer):
    editor_name = serializers.CharField(source="editor.get_full_name", read_only=True)

    class Meta:
        model = PageVersion
        fields = [
            "id",
            "version_number",
            "title",
            "body",
            "editor",
            "editor_name",
            "change_note",
            "created_at",
        ]
        read_only_fields = ["version_number", "created_at", "editor", "editor_name"]


class PagePreviewTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagePreviewToken
        fields = ["id", "token", "expires_at", "created_at"]
        read_only_fields = ["id", "token", "created_at"]


class PageSerializer(serializers.ModelSerializer):
    meta = PageMetaSerializer(required=False)
    sections = PageSectionSerializer(many=True, required=False)
    media = PageMediaSerializer(many=True, required=False)
    versions = PageVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = [
            "id",
            "title",
            "slug",
            "language_code",
            "body",
            "banner_image",
            "template",
            "status",
            "is_featured",
            "published_at",
            "unpublished_at",
            "is_deleted",
            "translated_from",
            "created_at",
            "updated_at",
            "meta",
            "sections",
            "media",
            "versions",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        meta_data = validated_data.pop("meta", None)
        sections_data = validated_data.pop("sections", [])
        media_data = validated_data.pop("media", [])

        with transaction.atomic():
            page = Page(**validated_data)
            page.full_clean()
            page.save()

            if meta_data:
                meta = PageMeta(page=page, **meta_data)
                meta.full_clean()
                meta.save()

            for section in sections_data:
                sec = PageSection(
                    page=page, **{k: v for k, v in section.items() if k != "id"}
                )
                sec.full_clean()
                sec.save()

            for media in media_data:
                med = PageMedia(
                    page=page, **{k: v for k, v in media.items() if k != "id"}
                )
                med.full_clean()
                med.save()
        return page

    def update(self, instance, validated_data):
        meta_data = validated_data.pop("meta", None)
        sections_data = validated_data.pop("sections", [])
        media_data = validated_data.pop("media", [])

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.full_clean()
            instance.save()

            if meta_data is not None:
                meta, _created = PageMeta.objects.get_or_create(page=instance)
                for attr, value in meta_data.items():
                    setattr(meta, attr, value)
                meta.full_clean()
                meta.save()

            existing_sections = {str(s.id): s for s in instance.sections.all()}
            payload_ids = set()
            for section in sections_data:
                sid = str(section.get("id") or "")
                data = {k: v for k, v in section.items() if k != "id"}
                if sid and sid in existing_sections:
                    sec = existing_sections[sid]
                    for k, v in data.items():
                        setattr(sec, k, v)
                    sec.full_clean()
                    sec.save()
                    payload_ids.add(sid)
                else:
                    sec = PageSection(page=instance, **data)
                    sec.full_clean()
                    sec.save()
                    payload_ids.add(str(sec.id))

            for sid, obj in existing_sections.items():
                if sid not in payload_ids:
                    obj.delete()

            existing_media = {str(m.id): m for m in instance.media.all()}
            payload_media_ids = set()
            for media in media_data:
                mid = str(media.get("id") or "")
                data = {k: v for k, v in media.items() if k != "id"}
                if mid and mid in existing_media:
                    med = existing_media[mid]
                    for k, v in data.items():
                        setattr(med, k, v)
                    med.full_clean()
                    med.save()
                    payload_media_ids.add(str(med.id))
                else:
                    med = PageMedia(page=instance, **data)
                    med.full_clean()
                    med.save()
                    payload_media_ids.add(str(med.id))
            for mid, obj in existing_media.items():
                if mid not in payload_media_ids:
                    obj.delete()

        return instance

    def validate_body(self, value):
        return clean_html(value)


class PageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = [
            "id",
            "title",
            "slug",
            "language_code",
            "status",
            "is_featured",
            "published_at",
            "created_at",
            "updated_at",
        ]
