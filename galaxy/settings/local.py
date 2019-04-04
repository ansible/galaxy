from .testing import *


DATABASES = {
    'default': {
        'NAME': 'galaxy',
        'CONN_MAX_AGE': None,
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    }
}