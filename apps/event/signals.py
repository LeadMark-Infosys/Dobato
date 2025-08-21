from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.event.models import Event
from apps.qr.utils import generate_qr

@receiver(post_save, sender=Event)
def create_event_qr(sender, instance, created, **kwargs):
    if created:
        generate_qr(
            entity_type="event",
            entity_id=instance.id, 
            municipality=instance.municipality.unique_slug,  
            name=instance.title
        )
