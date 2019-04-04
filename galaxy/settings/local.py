from .testing import *  # noqa: F401,F403


DATABASES = {
    'default': {
        'NAME': 'galaxy',
        'CONN_MAX_AGE': None,
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    }
}
