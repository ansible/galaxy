import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'galaxy.settings.custom'

from galaxy.wsgi import application  # noqa
