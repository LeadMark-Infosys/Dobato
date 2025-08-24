from django.contrib import admin
from .models import Page, PageMeta, PageVersion, PageSection, PageMedia, PageSlugHistory


class PageMetaInline(admin.StackedInline):
    model = PageMeta
    extra = 0


class PageSectionInline(admin.TabularInline):
    model = PageSection
    extra = 0
    ordering = ["position"]


class PageMediaInline(admin.TabularInline):
    model = PageMedia
    extra = 0


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "slug",
        "municipality",
        "language_code",
        "status",
        "is_featured",
        "created_at",
    ]
    list_filter = ["status", "language_code", "is_featured", "municipality", "template"]
    search_fields = ["title", "slug", "body"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PageMetaInline, PageSectionInline, PageMediaInline]
    readonly_fields = ["id", "created_at", "updated_at"]

    fieldsets = (
        (
            "Basic",
            {"fields": ("title", "slug", "language_code", "status", "template")},
        ),
        ("Content", {"fields": ("body", "banner_image", "is_featured")}),
        ("Scheduling", {"fields": ("scheduled_publish_at", "scheduled_unpublish_at")}),
        ("Publish State", {"fields": ("published_at", "unpublished_at")}),
        ("Relations", {"fields": ("municipality", "translated_from")}),
        ("Meta", {"fields": ("created_by", "updated_by")}),
        (
            "System",
            {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(PageVersion)
class PageVersionAdmin(admin.ModelAdmin):
    list_display = ["page", "version_number", "editor", "created_at"]
    list_filter = ["created_at", "page__municipality"]
    search_fields = ["page__title", "title", "change_note"]
    readonly_fields = ["version_number", "created_at", "snapshot"]


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ["page", "title", "type", "position", "is_active"]
    list_filter = ["type", "is_active", "page__municipality"]
    search_fields = ["page__title", "title", "content"]
    ordering = ["page", "position"]


@admin.register(PageMedia)
class PageMediaAdmin(admin.ModelAdmin):
    list_display = ["page", "caption", "is_featured"]
    list_filter = ["is_featured", "page__municipality"]
    search_fields = ["page__title", "caption"]


@admin.register(PageSlugHistory)
class PageSlugHistoryAdmin(admin.ModelAdmin):
    list_display = ["page", "old_slug", "new_slug", "changed_at"]
    search_fields = ["old_slug", "new_slug", "page__title"]
    list_filter = ["page__municipality", "page__language_code"]
