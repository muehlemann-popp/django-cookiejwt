from django.apps import AppConfig


class DjangoCookieJWTConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cookiejwt"
    verbose_name = "Django Cookie JWT"

    def ready(self):
        try:
            import django_cookiejwt.schema  # noqa
        except ImportError:
            pass
