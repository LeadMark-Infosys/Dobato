from rest_framework import serializers
from .models import PageMeta, PageVersion, PageSection, PageMedia


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
