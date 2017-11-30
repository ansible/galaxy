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

"""
WSGI config for Galaxy project.
"""
import os

from django.core.wsgi import get_wsgi_application

from galaxy import prepare_env

# For public Galaxy, we need to default /etc/galaxy/settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'galaxy.settings.custom')

# Prepare the galaxy environment.
prepare_env()

# Return the default Django WSGI application.
application = get_wsgi_application()
