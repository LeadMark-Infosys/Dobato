from django.apps import AppConfig

class QrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.qr'

    def ready(self):
        import apps.qr.signals
