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
# Django settings for galaxy project.
"""
Production configuration file.

The following environment variables are supported:

* GALAXY_SECRET_KEY
* GALAXY_ALLOWED_HOSTS
* GALAXY_EMAIL_HOST
* GALAXY_DB_URL
* GALAXY_DB_NAME
* GALAXY_DB_USER
* GALAXY_DB_PASSWORD
* GALAXY_DB_HOST
* GALAXY_DB_PORT
* GALAXY_EMAIL_PORT
* GALAXY_EMAIL_USER
* GALAXY_EMAIL_PASSWORD
* GALAXY_RABBITMQ_HOST
* GALAXY_RABBITMQ_PORT
* GALAXY_RABBITMQ_USER
* GALAXY_RABBITMQ_PASSWORD
* GALAXY_ADMIN_PATH
* GALAXY_METRICS_ENABLED
* GALAXY_INFLUX_DB_HOST
* GALAXY_INFLUX_DB_PORT
* GALAXY_INFLUX_DB_USERNAME
* GALAXY_INFLUX_DB_PASSWORD
* GALAXY_INFLUX_DB_UI_EVENTS_DB_NAME
"""

import os
import dj_database_url

from . import include_settings
from .default import *  # noqa

from .default import LOGGING as default_logging


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


def _set_logging():
    log = default_logging
    log['filters']['request_id'] = {
        '()': 'log_request_id.filters.RequestIDFilter'
    }
    log['handlers']['console']['formatter'] = 'json'
    log['handlers']['console']['filters'] = ['request_id']
    log['loggers']['django_request'] = {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': True,
    }
    log['loggers']['galaxy.api.access'] = {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': True,
    }
    return log

# =========================================================
# Django Core Settings
# =========================================================


DEBUG = False

ALLOWED_HOSTS = os.environ.get('GALAXY_ALLOWED_HOSTS', '*').split(',')

# Database
# ---------------------------------------------------------

# Define GALAXY_DB_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
DATABASES = {}

if os.environ.get('GALAXY_DB_URL'):
    DATABASES['default'] = dj_database_url.config(
        env='GALAXY_DB_URL', conn_max_age=0)
else:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('GALAXY_DB_NAME', 'galaxy'),
        'USER': os.environ.get('GALAXY_DB_USER', 'galaxy'),
        'PASSWORD': os.environ.get('GALAXY_DB_PASSWORD', ''),
        'HOST': os.environ.get('GALAXY_DB_HOST', ''),
        'PORT': int(os.environ.get('GALAXY_DB_PORT', 5432)),
        'CONN_MAX_AGE': 0,
    }

# Create default alias for worker logging
DATABASES['logging'] = DATABASES['default'].copy()

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
]

ADMIN_URL_PATH = os.environ.get('GALAXY_ADMIN_PATH', 'admin')
ADMIN_URL_PATTERN = r'^{}/'.format(ADMIN_URL_PATH)

CONTENT_DOWNLOAD_DIR = '/var/lib/galaxy/downloads'

GITHUB_TASK_USERS = ['galaxytasks01', 'galaxytasks02', 'galaxytasks03',
                     'galaxytasks04', 'galaxytasks05']

# =========================================================
# Logging Configuration
# =========================================================

# https://github.com/dabapps/django-log-request-id

LOG_REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
GENERATE_REQUEST_ID_IF_NOT_IN_HEADER = True
REQUEST_ID_RESPONSE_HEADER = "X-REQUEST-ID"
# LOG_REQUESTS = True

LOGGING = _set_logging()

# =========================================================
# InfluxDB Settings
# =========================================================
INFLUX_DB_HOST = os.environ.get('GALAXY_INFLUX_DB_HOST', 'influxdb')
INFLUX_DB_PORT = os.environ.get('GALAXY_INFLUX_DB_PORT', '8086')
INFLUX_DB_USERNAME = os.environ.get('GALAXY_INFLUX_DB_USERNAME', 'admin')
INFLUX_DB_PASSWORD = os.environ.get('GALAXY_INFLUX_DB_PASSWORD', '')
INFLUX_DB_UI_EVENTS_DB_NAME = os.environ.get(
    'GALAXY_INFLUX_DB_UI_EVENTS_DB_NAME', 'galaxy_ui_events'
)


# =========================================================
# System Settings
# =========================================================
include_settings('/etc/galaxy/settings.py', scope=globals(), optional=True)


# =========================================================
# Domain Settings
# =========================================================
GALAXY_URL = 'https://{site}'
