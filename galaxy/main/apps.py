#
#  When the application load initialize:
#    - signal/handlers
#    - elasticsearch-dsl default connection

from django.apps import AppConfig
from elasticsearch_dsl import connections
from django.conf import settings

class MainConfig(AppConfig):
    name = 'galaxy.main'
    verbose_name = "Galaxy"

    def ready(self):
        connections.connections.create_connection(hosts=settings.ELASTICSEARCH['hosts'], timeout=20)
        import galaxy.main.signals.handlers   # noqa
