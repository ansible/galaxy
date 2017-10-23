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

from .default import *  # noqa

# =========================================================
# Django Core Settings
# =========================================================

DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
# ---------------------------------------------------------

INSTALLED_APPS += (
    'autofixture',
    'debug_toolbar',
)

# Database
# ---------------------------------------------------------

# TODO(cutwater): Replace with DATABASE_URL connection string parameter
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'galaxy',
        'USER': 'galaxy',
        'PASSWORD': 'galaxy',
        'HOST': 'postgres',
        'PORT': 5432,
        'CONN_MAX_AGE': None,
    }
}

# Email settings
# ---------------------------------------------------------

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'

EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'var', 'email')

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

BROKER_URL = 'amqp://galaxy:galaxy@rabbit:5672/galaxy'

# =========================================================
# Galaxy Settings
# =========================================================

SITE_ENV = 'DEV'

SITE_NAME = 'localhost'

WAIT_FOR = [
    {'host': 'postgres', 'port': 5432},
    {'host': 'rabbit', 'port': 5672},
    {'host': 'memcache', 'port': 11211},
    {'host': 'elastic', 'port': 9200}
]
