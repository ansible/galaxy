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

import os
import sys
import mimetypes

from galaxy.common import version

__all__ = ['__version__']
__version__ = version.get_package_version(__name__)


def prepare_env():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'galaxy.settings.default')
    from django.conf import settings
    settings.version = __version__
    _fix_mimetypes()


def manage():
    prepare_env()

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


def _fix_mimetypes():
    mimetypes.add_type("image/svg+xml", ".svg", True)
    mimetypes.add_type("image/svg+xml", ".svgz", True)
