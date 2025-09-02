import qrcode
import os
from django.conf import settings
from apps.qr.models import QR
import uuid

def generate_qr(entity_type, entity_id, name=None, description=None, municipality="default", user=None):
    """
    Create and save a QR code for any entity (event, place, business, etc.)
    Stores only the file path in qr_code_image (TextField).
    """

    qr_instance = QR.objects.create(
        entity_type=entity_type,
        entity_id=entity_id,
        name=name or f"{entity_type}_{entity_id}",
        description=description or "",
        user=user
    )

    qr_url = f"https://{municipality}.dobato.net/qr/{entity_type}/{entity_id}/{qr_instance.uuid}/"

    qr_img = qrcode.make(qr_url)

    filename = f"{entity_type}_{entity_id}_{uuid.uuid4().hex}.png"
    folder = os.path.join(settings.MEDIA_ROOT, "qr_codes")
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    qr_img.save(filepath)

    qr_instance.qr_code_image = f"qr_codes/{filename}"
    qr_instance.save()

    return qr_instance
