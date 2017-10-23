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

import inspect

from .default import *  # noqa


def _read_secret_key(settings_dir='/etc/galaxy'):
    """
    Reads secret key from environment variable, otherwise from SECRET_KEY
    frile in settings directory.

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
    except OSError:
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

# Database
# ---------------------------------------------------------

# TODO(cutwater): Replace with DATABASE_URL connection string parameter
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME', 'galaxy'),
        'USER': os.environ.get('DATABASE_USER', 'galaxy'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', ''),
        'PORT': os.environ.get('DATABASE_PORT', 5432),
        'CONN_MAX_AGE': None,
    }
}

# Security
# ---------------------------------------------------------

SECRET_KEY = _read_secret_key()

# Email settings
# ---------------------------------------------------------

# FIXME(cutwater): Review parameters usage
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')

EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)

EMAIL_HOST_USER = os.environ.get('EMAIL_USER', '')

EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')

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
            '{0}:{1}'.format(os.environ.get('ELASTICSEARCH_HOST'),
                             os.environ.get('ELASTICSEARCH_PORT'))
        ],
    },
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'galaxy.main.elasticsearch_backend'
                  '.ElasticsearchSearchEngine',
        'URL': [
            'http://{0}:{1}'.format(os.environ.get('ELASTICSEARCH_HOST'),
                                    os.environ.get('ELASTICSEARCH_PORT'))
        ],
        'INDEX_NAME': 'haystack',
    },
}

# Celery settings
# ---------------------------------------------------------

# TODO(cutwater): Replace with BROKER_URL connection string parameter
BROKER_URL = 'amqp://{user}:{password}@{host}:{port}/{vhost}'.format(
    user=os.environ.get('RABBITMQ_USER', 'galaxy'),
    password=os.environ.get('RABBITMQ_PASSWORD', ''),
    host=os.environ.get('RABBITMQ_HOST', ''),
    port=os.environ.get('RABBITMQ_PORT', 5672),
    vhost=os.environ.get('RABBITMQ_VHOST', 'galaxy'),
)

# =========================================================
# Galaxy Settings
# =========================================================

SITE_ENV = 'PROD'

SITE_NAME = os.environ.get('GALAXY_SITE_NAME', 'localhost')

# =========================================================
# System Settings
# =========================================================

_include_settings('/etc/galaxy/settings.py', scope=globals(), optional=True)
