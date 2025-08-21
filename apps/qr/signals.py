from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import QRAnalytics

@receiver(post_save, sender=QRAnalytics)
def update_qr_scan_stats(sender, instance, created, **kwargs):
    if not created:
        return
    qr = instance.qr
    ip_address = instance.ip_address
    qr.total_scans += 1
    unique_ip_count = QRAnalytics.objects.filter(qr=qr, ip_address=ip_address).count()
    if unique_ip_count == 1:
        qr.unique_ip_count += 1
    qr.last_scanned_at = now()
    qr.save()
