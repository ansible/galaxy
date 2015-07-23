# Django settings for ansible galaxy project.

import os
import djcelery

djcelery.setup_loader()

DEBUG = True
TEMPLATE_DEBUG = DEBUG

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ADMINS = (
)

SITE_ENV="PROD"
SITE_NAME="galaxy.sngx.net"
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LOGIN_URL='/accounts/login/'
LOGOUT_URL='/'

EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT=587
EMAIL_HOST_USER="noreply@ansibleworks.com"
EMAIL_HOST_PASSWORD="7zMaXeblj5uphKIHeulv"
EMAIL_USE_TLS=True

AUTH_USER_MODEL = 'accounts.CustomUser'

# Settings for django-allauth
ACCOUNT_AUTHENTICATION_METHOD="username_email"
ACCOUNT_DEFAULT_HTTP_PROTOCOL="https"
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL="/accounts/profile/"
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL="/accounts/landing"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS=1
ACCOUNT_EMAIL_REQUIRED=True
ACCOUNT_EMAIL_VERIFICATION="mandatory"
ACCOUNT_EMAIL_SUBJECT_PREFIX="AnsibleWorks Galaxy "
ACCOUNT_LOGIN_ON_VALIDATE=True
ACCOUNT_USERNAME_MIN_LENGTH=6
ACCOUNT_USERNAME_BLACKLIST=['admin','administrator']
ACCOUNT_PASSWORD_MIN_LENGTH=8
SOCIALACCOUNT_PROVIDERS={
    'twitter': { 'SCOPE': ['r_emailaddress'] },
}
SOCIALACCOUNT_AVATAR_SUPPORT=True

# Settings for celery/rabbitmq
BROKER_URL='amqp://galaxy:galaxy@localhost:5672/galaxy'
CELERY_IMPORTS=('galaxy.main.celerytasks.tasks',)
CELERY_TRACK_STARTED=True
CELERYBEAT_SCHEDULER='djcelery.schedulers.DatabaseScheduler'

# Settings for Github API (pygithub)
GITHUB_USERNAME=''
GITHUB_PASSWORD=''

# Custom settings
GALAXY_COMMENTS_THRESHOLD=10.0

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'galaxy',
        'USER': 'galaxy',
        'PASSWORD': 'galaxy',
        'HOST': 'localhost',
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_SAVE_EVERY_REQUEST = True

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'DEFAULT_PAGINATION_SERIALIZER_CLASS': 'galaxy.api.pagination.PaginationSerializer',
    'DEFAULT_FILTER_BACKENDS': (
        'galaxy.api.filters.ActiveOnlyBackend',
        'galaxy.api.filters.FieldLookupBackend',
        'rest_framework.filters.SearchFilter',
        'galaxy.api.filters.OrderByBackend',
    ),
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [SITE_NAME]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = '/var/lib/galaxy/public/static'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'galaxy', 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = file('/etc/galaxy/SECRET_KEY', 'rb').read().strip()

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'galaxy.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'galaxy.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'galaxy', 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',
    'autofixture',
    'avatar',
    'bootstrapform',
    'djcelery',
    'rest_framework',
    # our apps
    'galaxy.accounts',
    'galaxy.main',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount',
)

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

