from django.apps import AppConfig


class TourismConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tourism'

    def ready(self):
        import apps.tourism.signals
