# (c) 2012-2018, Ansible by Red Hat
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by
# the Apache Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Apache License for more details.
#
# You should have received a copy of the Apache License
# along with Galaxy.  If not, see <http://www.apache.org/licenses/>.


import logging

from django.conf import settings
from django.db.migrations.executor import MigrationExecutor
from django.db import connections, DatabaseError, DEFAULT_DB_ALIAS
import influxdb.client
import kombu
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests.exceptions
import redis

from galaxy.api.views import base_views


__all__ = [
    'MonitorRootView',
]

logger = logging.getLogger(__name__)


def get_influx_status():
    if not settings.GALAXY_METRICS_ENABLED:
        return None

    client = influxdb.InfluxDBClient(
        host=settings.INFLUX_DB_HOST,
        port=settings.INFLUX_DB_PORT,
        username=settings.INFLUX_DB_USERNAME,
        password=settings.INFLUX_DB_PASSWORD,
        timeout=5,
        retries=1,
    )

    try:
        client.ping()
    except (
            influxdb.client.InfluxDBClientError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout
    ):
        return 'error'
    except Exception:
        logger.exception('Unexpected error when trying to connect to InfluxDB')
        return 'error'
    finally:
        client.close()
    return 'ok'


def get_postgres_status():
    status = 'ok'
    migrations = 'ok'
    try:
        connection = connections[DEFAULT_DB_ALIAS]
        connection.prepare_database()
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        if executor.migration_plan(targets):
            migrations = 'needed'
    except DatabaseError:
        status = 'error'
    except Exception:
        logger.exception('Unexpected error when trying to connect to Postgres')
        status = 'error'
    return status, migrations


def get_redis_status():
    client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT
    )
    try:
        client.ping()
    except redis.RedisError:
        return 'error'
    except Exception:
        logger.exception('Unexpected error when trying to connect to Redis')
        return 'error'
    finally:
        del client
    return 'ok'


def get_rabbit_status():
    client = kombu.Connection(settings.BROKER_URL)
    try:
        client.connect()
    except client.connection_errors:
        return 'error'
    except Exception:
        logger.exception('Unexpected error when trying to connect to Rabbit')
        return 'error'
    finally:
        client.close()
    return 'ok'


class MonitorRootView(base_views.APIView):
    """ Monitor resources """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        response = {
            'influx': get_influx_status(),
            'migrations': None,
            'postgresql': None,
            'rabbit': get_rabbit_status(),
            'redis': get_redis_status()
        }
        (response['postgresql'], response['migrations']) = \
            get_postgres_status()
        return Response(response)
