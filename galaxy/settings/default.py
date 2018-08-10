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

import os

import djcelery


djcelery.setup_loader()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

# =========================================================
# Django Core Settings
# =========================================================

DEBUG = False

ALLOWED_HOSTS = []

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

SITE_ID = 1

# Application definition
# ---------------------------------------------------------

# TODO(cutwater): Review 3rd party apps usage
INSTALLED_APPS = (
    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',

    # Allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',

    # 3rd part apps
    'bootstrapform',
    'djcelery',
    'rest_framework',
    'rest_framework.authtoken',

    # Project apps
    'galaxy.accounts',
    'galaxy.main',
)

# FIXME(cutwater): Deprecated from Django 1.10, use MIDDLEWARE setting
# instead.
MIDDLEWARE_CLASSES = (
    'log_request_id.middleware.RequestIDMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'galaxy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'galaxy', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'galaxy.wsgi.application'

# Authentication
# ---------------------------------------------------------

AUTHENTICATION_BACKENDS = (
    # Required for login by username in Django admin
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

AUTH_USER_MODEL = 'accounts.CustomUser'

LOGIN_URL = '/accounts/login/'

LOGIN_REDIRECT_URL = '/home'

# Sessions
# ---------------------------------------------------------

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SESSION_SAVE_EVERY_REQUEST = True

# Security
# ---------------------------------------------------------

# SECURITY WARNING: Use unique key in production and keep it secret!
SECRET_KEY = '+^b03*zldz4fd!p%asz+(8u8b-0#6uw4eaex0xf$3w-km%)&2y'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Internationalization
# ---------------------------------------------------------

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files
# ---------------------------------------------------------

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'build', 'static')

# Database
# ---------------------------------------------------------

DATABASES = {}

# =========================================================
# Third Party Apps Settings
# =========================================================


# Rest Framework
# ---------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'galaxy.api.permissions.ModelAccessPermission',
    ),
    # TODO(cutwater): Update production settings
    'DEFAULT_PAGINATION_CLASS':
        'galaxy.api.pagination.PageNumberPagination',
    'DEFAULT_FILTER_BACKENDS': (
        'galaxy.api.filters.ActiveOnlyBackend',
        'galaxy.api.filters.FieldLookupBackend',
        'rest_framework.filters.SearchFilter',
        'galaxy.api.filters.OrderByBackend',
    ),
}

# Celery
# ---------------------------------------------------------

BROKER_URL = None

CELERY_IMPORTS = (
    'galaxy.main.celerytasks.tasks',
    'galaxy.worker.tasks',
)

CELERY_TRACK_STARTED = True

CELERY_TASK_SERIALIZER = 'json'

CELERY_ACCEPT_CONTENT = ['json']

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

# Allauth
# ---------------------------------------------------------

ACCOUNT_ADAPTER = 'galaxy.main.auth.AccountAdapter'

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/accounts/profile/'

ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/accounts/landing'

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1

ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_EMAIL_VERIFICATION = 'none'

ACCOUNT_EMAIL_SUBJECT_PREFIX = 'Ansible Galaxy '

ACCOUNT_LOGIN_ON_VALIDATE = True

ACCOUNT_USERNAME_MIN_LENGTH = 3

ACCOUNT_USERNAME_BLACKLIST = (
    'admin',
    'administrator',
    'galaxy_admin',
    'accounts',
    'account',
    'explore',
    'intro',
    'list',
    'detail',
    'roleadd',
    'imports',
    'authors',
)

ACCOUNT_PASSWORD_MIN_LENGTH = 8

SOCIALACCOUNT_PROVIDERS = {
    'twitter': {
        'SCOPE': ['r_emailaddress']
    },
    'github': {
        'SCOPE': ['user:email', 'public_repo', 'read:org']
    },
}

SOCIALACCOUNT_AVATAR_SUPPORT = True

# =========================================================
# Galaxy Settings
# =========================================================

# TODO(cutwater): Parameters description required
GITHUB_TASK_USERS = []

GITHUB_SERVER = 'https://api.github.com'

GALAXY_COMMENTS_THRESHOLD = 10.0

SITE_ENV = 'PROD'

SITE_NAME = 'localhost'

TRAVIS_CONFIG_URL = 'https://api.travis-ci.org/config'

# TODO(cutwater): Consider removing wait_for from settings
WAIT_FOR = []

ADMIN_URL_PATH = 'admin'
ADMIN_URL_PATTERN = r'^{}/'.format(ADMIN_URL_PATH)

ROLE_TYPES_ENABLED = frozenset(['ANS', 'CON', 'APP'])

CONTENT_DOWNLOAD_DIR = None
"""
A base directory used by repository import task to clone repositories into.

If set to `None`, system temporary directory is used.
"""

# =========================================================
# Logging
# =========================================================

# LOGS_DIR = os.path.join(BASE_DIR, 'var', 'log')

# TODO(cutwater): Adjust logging config for production environment
# TODO(cutwater): Review logging config
LOGGING = {
    'version': 1,

    'disable_existing_loggers': False,

    'formatters': {
        'json': {
            '()': 'jog.JogFormatter',
            'format': ('%(asctime)s %(request_id)s %(levelname)s] '
                       '%(module)s: %(message)s'),
        },
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(module)s: %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'request_id': {
            '()': 'log_request_id.filters.RequestIDFilter'
        },
    },

    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'import_task': {
            'level': 'DEBUG',
            'class': 'galaxy.common.logutils.ImportTaskHandler',
            'formatter': 'simple',
        }
    },

    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'galaxy.api': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'galaxy.accounts': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'galaxy.main': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'galaxy.worker': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'galaxy.worker.tasks.import_repository': {
            'handlers': ['import_task'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'allauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
