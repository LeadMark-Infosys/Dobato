from rest_framework import serializers
from .models import PageMeta, PageVersion, PageSection, PageMedia, Page


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


class PageMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageMedia
        fields = ["id", "media_url", "caption", "is_featured"]


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
        read_only_fields = ["version_number", "created_at"]


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
            meta, created = PageMeta.objects.get_or_create(page=instance)
            for attr, value in meta_data.items():
                setattr(meta, attr, value)
            meta.save()

        if sections_data:
            instance.sections.all().delete()
            for section in sections_data:
                PageSection.objects.create(page=instance, **section)

        if media_data:
            instance.media.all().delete()
            for media in media_data:
                PageMedia.objects.create(page=instance, **media)

        return instance


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
