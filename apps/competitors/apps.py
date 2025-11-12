from django.apps import AppConfig


class CompetitorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.competitors"

    def ready(self):
        import apps.competitors.competitor_review.signals
