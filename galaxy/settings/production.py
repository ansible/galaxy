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
* GALAXY_DB_NAME
* GALAXY_DB_USER
* GALAXY_DB_PASSWORD
* GALAXY_DB_HOST
* GALAXY_DB_PORT
* GALAXY_EMAIL_HOST
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
"""

import os
import inspect

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


def _include_settings(filename, scope=None, optional=False):
    """
    Includes python settings file into specified scope.

    :param str filename: Python source file.
    :param scope: Destination scope, by default global scope of function caller
           is used.
    :param bool optional: If set to True no exception will be raised if
           file does not exist.
    """
    if scope is None:
        scope = inspect.stack()[1][0].f_globals

    try:
        fp = open(filename)
    except IOError:
        if optional:
            return
        raise

    with fp:
        exec(fp.read(), scope)


# =========================================================
# Django Core Settings
# =========================================================

DEBUG = False

ALLOWED_HOSTS = os.environ.get('GALAXY_ALLOWED_HOSTS', '*').split(',')

# Database
# ---------------------------------------------------------

# TODO(cutwater): Replace with DATABASE_URL connection string parameter
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('GALAXY_DB_NAME', 'galaxy'),
        'USER': os.environ.get('GALAXY_DB_USER', 'galaxy'),
        'PASSWORD': os.environ.get('GALAXY_DB_PASSWORD', ''),
        'HOST': os.environ.get('GALAXY_DB_HOST', ''),
        'PORT': int(os.environ.get('GALAXY_DB_PORT', 5432)),
        'CONN_MAX_AGE': None,
    }
}

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
                os.environ.get('GALAXY_ELASTICSEARCH_PORT'))
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
                os.environ.get('GALAXY_ELASTICSEARCH_PORT'))
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
        'host': os.environ.get('GALAXY_DB_HOST', ''),
        'port': int(os.environ.get('GALAXY_DB_PORT', 5432)),
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
        'host': os.environ.get('GALAXY_ELASTICSEARCH_HOST'),
        'port': int(os.environ.get('GALAXY_ELASTICSEARCH_PORT', 9200)),
    }
]

# =========================================================
# Logging
# =========================================================

LOGS_DIR = '/var/log/galaxy'

LOGGING['handlers']['allauth_logfile']['filename'] = (  # noqa: F405
    os.path.join(LOGS_DIR, 'allauth.log'))
LOGGING['handlers']['django_logfile']['filename'] = (  # noqa: F405
    os.path.join(LOGS_DIR, 'django.log'))
LOGGING['handlers']['galaxy_logfile']['filename'] = (  # noqa: F405
    os.path.join(LOGS_DIR, 'galaxy.log'))

# =========================================================
# System Settings
# =========================================================

_include_settings('/etc/galaxy/settings.py', scope=globals(), optional=True)
