from django.apps import AppConfig


class AgentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts_app'

    def ready(self):
        import accounts_app.signals
