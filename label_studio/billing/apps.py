from django.apps import AppConfig


class BillingConfig(AppConfig):
    name = "billing"
    verbose_name = "Billing"

    def ready(self):
        # Import signal handlers
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid import-time failures during certain commands
            pass


