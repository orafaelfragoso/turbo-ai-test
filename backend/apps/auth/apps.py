from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auth"
    label = "apps_auth"
    verbose_name = "Authentication"

    def ready(self):
        """
        Import schema extensions when the app is ready.
        This ensures drf-spectacular can discover our custom authentication scheme.
        """
        # Import to register the OpenAPI authentication extension
        from . import schema  # noqa: F401
