from celery import shared_task
from django.utils import timezone
from django.db import transaction
from apps.cms.models import Page

@shared_task(name="cms.publish_unpublish_scheduled_pages")
def publish_unpublish_scheduled_pages():
    now = timezone.now()
    with transaction.atomic():
        published = Page.objects.filter(
            status__in=["draft", "pending"],
            published_at__isnull=False,
            published_at__lte=now,
        ).update(status="published")
        unpublished = Page.objects.filter(
            status="published",
            unpublished_at__isnull=False,
            unpublished_at__lte=now,
        ).update(status="draft")
    return {"published": published, "unpublished": unpublished}
