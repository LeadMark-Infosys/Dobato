from celery import shared_task
from django.utils import timezone
from .models import Page


@shared_task(name="cms.publish_unpublish_scheduled_pages")
def publish_unpublish_scheduled_pages():
    now = timezone.now()
    to_publish = Page.objects.filter(
        status__in=["draft", "pending"],
        scheduled_publish_at__isnull=False,
        scheduled_publish_at__lte=now,
        is_deleted=False,
    )
    for p in to_publish:
        p.status = "published"
        if not p.published_at:
            p.published_at = now
        p.save()

    to_unpublish = Page.objects.filter(
        status="published",
        scheduled_unpublish_at__isnull=False,
        scheduled_unpublish_at__lte=now,
        is_deleted=False,
    )
    for p in to_unpublish:
        p.status = "archived"
        p.save()
