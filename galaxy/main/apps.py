
from django.apps import AppConfig

class MainConfig(AppConfig):
    name = 'galaxy.main'
    verbose_name = "Galaxy"

    def ready(self):
        print ('foo!')
        import galaxy.main.signals.handlers