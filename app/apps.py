from django.apps import AppConfig

from recipe_track.scheduler import start


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        start()
