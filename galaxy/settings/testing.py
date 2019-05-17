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

# FIXME: This module is copy-paste of dev settings. It needs review and fixes.

import os

from .default import *  # noqa


# =========================================================
# Django Core Settings
# =========================================================

DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# ---------------------------------------------------------

DATABASES = {
    'default': {
        'NAME': 'galaxy',
        'USER': 'galaxy',
        'PASSWORD': 'galaxy',
        'HOST': 'postgres',
        'PORT': 5432,
        'CONN_MAX_AGE': None,
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    }
}

# Create default alias for worker logging
DATABASES['logging'] = DATABASES['default'].copy()

# Set the test database name
DATABASES['default']['TEST'] = {'NAME': 'test_galaxy'}
DATABASES['logging']['TEST'] = {'NAME': 'test_galaxy'}

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
]

STATIC_ROOT = ''

MEDIA_ROOT = '/var/lib/galaxy/media/'
