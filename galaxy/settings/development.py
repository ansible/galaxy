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

import os
import dj_database_url

from .default import *  # noqa


# =========================================================
# Django Core Settings
# =========================================================

DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
# ---------------------------------------------------------

INSTALLED_APPS += (  # noqa: F405
    'autofixture',
    'debug_toolbar',
)

# Database
# ---------------------------------------------------------

# Define DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
DATABASES = {'default': dj_database_url.config(default='postgres://galaxy:galaxy@postgres:5432/galaxy', conn_max_age=None)} 

# Set the test database name 
DATABASES['default']['TEST'] = {'NAME': 'galaxy'} 

# Cache
# ---------------------------------------------------------

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'memcache:11211',
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

# Email settings
# ---------------------------------------------------------

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'

EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'var', 'email')  # noqa: F405

# =========================================================
# Third Party Apps Settings
# =========================================================

# Debug Toolbar
# ---------------------------------------------------------

DEBUG_TOOLBAR_PATCH_SETTINGS = False

# Elasticsearch settings
# ---------------------------------------------------------

ELASTICSEARCH = {
    'default': {
        'hosts': ["elastic:9200"],
        'timeout': 20,
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'galaxy.main.elasticsearch_backend'
                  '.ElasticsearchSearchEngine',
        'URL': ['http://elastic:9200'],
        'INDEX_NAME': 'haystack',
    },
}

# Celery settings
# ---------------------------------------------------------

BROKER_URL = 'amqp://galaxy:galaxy@rabbitmq:5672/galaxy'

# =========================================================
# Galaxy Settings
# =========================================================

SITE_ENV = 'DEV'

SITE_NAME = 'localhost'

WAIT_FOR = [
    {'host': 'postgres', 'port': 5432},
    {'host': 'rabbitmq', 'port': 5672},
    {'host': 'memcache', 'port': 11211},
    {'host': 'elastic', 'port': 9200}
]
