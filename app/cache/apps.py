from django.apps import AppConfig


class CacheConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.cache"
    verbose_name = "Cache Functionality"

    def ready(self):
        # Custom app-specific initialization
        print("cache app is ready!")
