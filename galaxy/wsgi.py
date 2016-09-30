# (c) 2012-2016, Ansible by Red Hat
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

from galaxy import prepare_env
from django.core.wsgi import get_wsgi_application
from galaxy.settings import WAIT_FOR

import socket
import time
import logging

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

logger = logging.getLogger('galaxy.main')

for service in WAIT_FOR:
    is_alive = False
    count = 0
    while not is_alive and count < 10:
        count += 1
        logger.info("Waiting on %s:%s" % (service['host'], service['port']))
        try:
            s.connect((service['host'], service['port']))
        except socket.error as exc:
            if "endpoint is already connected" in str(exc):
                is_alive = True
            else:
                time.sleep(1)
        else:
            is_alive = True

# Prepare the galaxy environment.
prepare_env()

# Return the default Django WSGI application.
application = get_wsgi_application()

