from rest_framework import serializers
from django.db import IntegrityError, DatabaseError
from urllib.parse import urlparse
from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
import logging
import bleach

from .models import (
    PageMeta,
    PageVersion,
    PageSection,
    PageMedia,
    Page,
    PagePreviewToken,
)

log = logging.getLogger(__name__)

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


def clean_html(v: str) -> str:
    return bleach.clean(
        v or "",
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def sanitize_meta_text(v: str) -> str:
    return bleach.clean(
        v or "", tags=[], attributes={}, protocols=ALLOWED_PROTOCOLS, strip=True
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
        p = urlparse(v)
        if not p.scheme or not p.netloc:
            raise serializers.ValidationError("Canonical URL must be absolute.")
        if p.scheme not in ("http", "https"):
            raise serializers.ValidationError("Canonical URL must be http or https.")
        if (
            getattr(settings, "CMS_ENFORCE_HTTPS_CANONICAL", True)
            and p.scheme != "https"
        ):
            raise serializers.ValidationError("HTTPS required for canonical URL.")
        return v

    def validate(self, attrs):
        for k in list(attrs.keys()):
            if isinstance(attrs[k], str):
                attrs[k] = sanitize_meta_text(attrs[k])
        return attrs


class PageSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageSection
        fields = ["id", "title", "content", "type", "position", "is_active"]
        read_only_fields = ["id"]

    def validate_content(self, v):
        return clean_html(v)


class PageMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageMedia
        fields = ["id", "media_url", "url", "file", "caption", "is_featured"]
        read_only_fields = ["id"]

    def _validate_http(self, v, name):
        if not v:
            return v
        try:
            URLValidator(schemes=["http", "https"])(v)
        except DjangoValidationError:
            raise serializers.ValidationError(f"Invalid {name} (http/https only).")
        return v

    def validate_url(self, v):
        return self._validate_http(v, "url")

    def validate_media_url(self, v):
        return self._validate_http(v, "media_url")

    def validate(self, attrs):
        url = attrs.get("url") or getattr(self.instance, "url", "")
        media_url = attrs.get("media_url") or getattr(self.instance, "media_url", "")
        file = attrs.get("file") or getattr(self.instance, "file", None)
        if not (file or url or media_url):
            raise serializers.ValidationError(
                {"non_field_errors": ["Provide file, url or media_url."]}
            )
        if "caption" in attrs and isinstance(attrs["caption"], str):
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

    def _municipality_from_request(self):
        req = self.context.get("request")
        return getattr(req, "tenant", None) if req else None

    def _map_db_error(self, err):
        msg = str(err)
        if "unique_page_slug_active" in msg or (
            "slug" in msg and "UNIQUE" in msg.upper()
        ):
            return {
                "slug": "This slug is already used for this municipality and language."
            }
        return {"detail": "Database error: " + msg}

    def validate(self, attrs):
        attrs = super().validate(attrs)
        muni = self._municipality_from_request()
        if muni and not self.instance:
            attrs.setdefault("municipality", muni)
        slug = attrs.get("slug") or (self.instance.slug if self.instance else None)
        lang = attrs.get("language_code") or (
            self.instance.language_code if self.instance else None
        )
        if muni and slug and lang:
            qs = Page.objects.filter(
                municipality=muni, slug=slug, language_code=lang, is_deleted=False
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {
                        "slug": "This slug is already used for this municipality and language."
                    }
                )
        return attrs

    def validate_body(self, v):
        return clean_html(v)

    def _save_obj(self, obj, ctx_key):
        try:
            obj.full_clean()
            obj.save()
        except DjangoValidationError as e:
            raise serializers.ValidationError({ctx_key: e.message_dict})
        except (IntegrityError, DatabaseError) as e:
            log.exception("DB error saving %s", ctx_key)
            raise serializers.ValidationError({ctx_key: self._map_db_error(e)})

    def create(self, validated_data):
        meta_data = validated_data.pop("meta", None)
        sections_data = validated_data.pop("sections", [])
        media_data = validated_data.pop("media", [])
        page = Page(**validated_data)
        try:
            page.full_clean()
            page.save()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        except (IntegrityError, DatabaseError) as e:
            raise serializers.ValidationError(self._map_db_error(e))
        if meta_data:
            self._save_obj(PageMeta(page=page, **meta_data), "meta")
        for s in sections_data:
            self._save_obj(
                PageSection(page=page, **{k: v for k, v in s.items() if k != "id"}),
                "sections",
            )
        for m in media_data:
            self._save_obj(
                PageMedia(page=page, **{k: v for k, v in m.items() if k != "id"}),
                "media",
            )
        return page

    def update(self, instance, validated_data):
        meta_data = validated_data.pop("meta", None)
        sections_data = validated_data.pop("sections", [])
        media_data = validated_data.pop("media", [])
        for k, v in validated_data.items():
            setattr(instance, k, v)
        try:
            instance.full_clean()
            instance.save()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        except (IntegrityError, DatabaseError) as e:
            raise serializers.ValidationError(self._map_db_error(e))
        if meta_data is not None:
            meta, _ = PageMeta.objects.get_or_create(page=instance)
            for k, v in meta_data.items():
                setattr(meta, k, v)
            self._save_obj(meta, "meta")
        existing_sections = {str(s.id): s for s in instance.sections.all()}
        keep = set()
        for s in sections_data:
            sid = str(s.get("id") or "")
            data = {k: v for k, v in s.items() if k != "id"}
            if sid and sid in existing_sections:
                sec = existing_sections[sid]
                for k, v in data.items():
                    setattr(sec, k, v)
            else:
                sec = PageSection(page=instance, **data)
            self._save_obj(sec, "sections")
            keep.add(str(sec.id))
        for sid, obj in existing_sections.items():
            if sid not in keep:
                obj.delete()
        existing_media = {str(m.id): m for m in instance.media.all()}
        keep_m = set()
        for m in media_data:
            mid = str(m.get("id") or "")
            data = {k: v for k, v in m.items() if k != "id"}
            if mid and mid in existing_media:
                med = existing_media[mid]
                for k, v in data.items():
                    setattr(med, k, v)
            else:
                med = PageMedia(page=instance, **data)
            self._save_obj(med, "media")
            keep_m.add(str(med.id))
        for mid, obj in existing_media.items():
            if mid not in keep_m:
                obj.delete()
        return instance


class PageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ["id", "title", "slug", "language_code", "status", "updated_at"]
