from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'reservations'

    def ready(self):
        # Signal for Activity Log
    	from . import signals