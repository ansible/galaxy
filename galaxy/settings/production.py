# (c) 2012-2017, Ansible by Red Hat
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
# Django settings for galaxy project.
"""
Production configuration file.

The following environment variables are supported:

* GALAXY_SECRET_KEY
* GALAXY_ALLOWED_HOSTS
* GALAXY_EMAIL_HOST
* DATABASE_URL    # from dj_database_url
* GALAXY_EMAIL_PORT
* GALAXY_EMAIL_USER
* GALAXY_EMAIL_PASSWORD
* GALAXY_ELASTICSEARCH_HOST
* GALAXY_ELASTICSEARCH_PORT
* GALAXY_MEMCACHE_HOST
* GALAXY_MEMCACHE_PORT
* GALAXY_RABBITMQ_HOST
* GALAXY_RABBITMQ_PORT
* GALAXY_RABBITMQ_USER
* GALAXY_RABBITMQ_PASSWORD
* GALAXY_ADMIN_PATH
"""

import os
import dj_database_url

from . import include_settings
from .default import *  # noqa


def _read_secret_key(settings_dir='/etc/galaxy'):
    """
    Reads secret key from environment variable, otherwise from SECRET_KEY
    file in settings directory.

    In case secret key cannot be read, function returns None, which
    causes django configuration exception.

    :param settings_dir: Settings directory, default: '/etc/galaxy'.
    :return: Secret key string, if available, None otherwise.
    """
    try:
        return os.environ['GALAXY_SECRET_KEY']
    except KeyError:
        pass

    try:
        with open(os.path.join(settings_dir, 'SECRET_KEY')) as fp:
            return fp.read().strip()
    except IOError:
        return None


# =========================================================
# Django Core Settings
# =========================================================

DEBUG = False

ALLOWED_HOSTS = os.environ.get('GALAXY_ALLOWED_HOSTS', '*').split(',')

# Database
# ---------------------------------------------------------

# Define DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME 
DATABASES = {'default': dj_database_url.config(conn_max_age=None)}

# Cache
# ---------------------------------------------------------

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '{0}:{1}'.format(
            os.environ.get('GALAXY_MEMCACHE_HOST', ''),
            os.environ.get('GALAXY_MEMCACHE_PORT', 11211)),
    },
    'download_count': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'main_download_count_cache',
        'TIMEOUT': None,
        'OPTIONS': {
            'MAX_ENTRIES': 100000,
            'CULL_FREQUENCY': 0
        }
    }
}

# Static files
# ---------------------------------------------------------

STATIC_ROOT = '/var/lib/galaxy/public/static'

# Security
# ---------------------------------------------------------

SECRET_KEY = _read_secret_key()

# Email settings
# ---------------------------------------------------------

# FIXME(cutwater): Review parameters usage
EMAIL_HOST = os.environ.get('GALAXY_EMAIL_HOST', '')

EMAIL_PORT = int(os.environ.get('GALAXY_EMAIL_PORT', 587))

EMAIL_HOST_USER = os.environ.get('GALAXY_EMAIL_USER', '')

EMAIL_HOST_PASSWORD = os.environ.get('GALAXY_EMAIL_PASSWORD', '')

EMAIL_USE_TLS = True

# =========================================================
# Third Party Apps Settings
# =========================================================

# Maintenance
# ---------------------------------------------------------

MAINTENANCE_MODE = False

MAINTENANCE_FILE = '/var/lib/galaxy/.maintenance'

# Elasticsearch settings
# ---------------------------------------------------------

ELASTICSEARCH = {
    'default': {
        'hosts': [
            '{0}:{1}'.format(
                os.environ.get('GALAXY_ELASTICSEARCH_HOST'),
                os.environ.get('GALAXY_ELASTICSEARCH_PORT', 9200))
        ],
    },
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'galaxy.main.elasticsearch_backend'
                  '.ElasticsearchSearchEngine',
        'URL': [
            'http://{0}:{1}'.format(
                os.environ.get('GALAXY_ELASTICSEARCH_HOST'),
                os.environ.get('GALAXY_ELASTICSEARCH_PORT', 9200))
        ],
        'INDEX_NAME': 'haystack',
    },
}

# Celery settings
# ---------------------------------------------------------

# TODO(cutwater): Replace with BROKER_URL connection string parameter
BROKER_URL = 'amqp://{user}:{password}@{host}:{port}/{vhost}'.format(
    user=os.environ.get('GALAXY_RABBITMQ_USER', 'galaxy'),
    password=os.environ.get('GALAXY_RABBITMQ_PASSWORD', ''),
    host=os.environ.get('GALAXY_RABBITMQ_HOST', ''),
    port=os.environ.get('GALAXY_RABBITMQ_PORT', 5672),
    vhost=os.environ.get('GALAXY_RABBITMQ_VHOST', 'galaxy'),
)

# =========================================================
# Galaxy Settings
# =========================================================

SITE_ENV = 'PROD'

SITE_NAME = os.environ.get('GALAXY_SITE_NAME', 'localhost')

# FIXME(cutwater): Remove WAIT_FOR logic from django application
WAIT_FOR = [
    {
        'host': DATABASES['default']['HOST'],
        'port': DATABASES['default']['PORT'],
    },
    {
        'host': os.environ.get('GALAXY_RABBITMQ_HOST', ''),
        'port': int(os.environ.get('GALAXY_RABBITMQ_PORT', 5672))
    },
    {
        'host': os.environ.get('GALAXY_MEMCACHE_HOST', ''),
        'port': int(os.environ.get('GALAXY_MEMCACHE_PORT', 11211))
    },
    {
        'host': os.environ.get('GALAXY_ELASTICSEARCH_HOST', ''),
        'port': int(os.environ.get('GALAXY_ELASTICSEARCH_PORT', 9200)),
    }
]

ADMIN_URL_PATTERN = r'^%s/' % os.environ.get('GALAXY_ADMIN_PATH', 'admin')

# =========================================================
# System Settings
# =========================================================

include_settings('/etc/galaxy/settings.py', scope=globals(), optional=True)
