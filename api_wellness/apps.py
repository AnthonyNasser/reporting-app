from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api_wellness'
    verbose_name = 'API Wellness'

    def ready(self):
        # Connect signals
    	from . import signals
