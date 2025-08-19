from rest_framework import serializers
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
        fields = ["id", "media_url", "caption", "is_featured"]
        read_only_fields = ["id"]


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

        page = Page.objects.create(**validated_data)

        if meta_data:
            PageMeta.objects.create(page=page, **meta_data)
        for section in sections_data:
            PageSection.objects.create(page=page, **section)
        for media in media_data:
            PageMedia.objects.create(page=page, **media)
        return page

    def update(self, instance, validated_data):
        meta_data = validated_data.pop("meta", None)
        sections_data = validated_data.pop("sections", [])
        media_data = validated_data.pop("media", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if meta_data:
            meta, _ = PageMeta.objects.get_or_create(page=instance)
            for attr, value in meta_data.items():
                setattr(meta, attr, value)
            meta.save()

        # Non-destructive sections
        existing_sections = {str(s.id): s for s in instance.sections.all()}
        seen_section_ids = set()
        for section in sections_data:
            sid = str(section.get("id") or "")
            data = {k: v for k, v in section.items() if k != "id"}
            if sid and sid in existing_sections:
                sec = existing_sections[sid]
                for k, v in data.items():
                    setattr(sec, k, v)
                sec.save()
                seen_section_ids.add(sid)
            else:
                new = PageSection.objects.create(page=instance, **data)
                seen_section_ids.add(str(new.id))
        # delete removed
        for sid, obj in existing_sections.items():
            if sid not in seen_section_ids:
                obj.delete()

        # Non-destructive media
        existing_media = {str(m.id): m for m in instance.media.all()}
        seen_media_ids = set()
        for media in media_data:
            mid = str(media.get("id") or "")
            data = {k: v for k, v in media.items() if k != "id"}
            if mid and mid in existing_media:
                med = existing_media[mid]
                for k, v in data.items():
                    setattr(med, k, v)
                med.save()
                seen_media_ids.add(mid)
            else:
                newm = PageMedia.objects.create(page=instance, **data)
                seen_media_ids.add(str(newm.id))
        for mid, obj in existing_media.items():
            if mid not in seen_media_ids:
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
