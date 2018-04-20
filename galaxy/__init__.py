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
import warnings
import mimetypes

from galaxy.common import version

__all__ = ['__version__']
__version__ = version.get_package_version(__name__)


def find_commands(management_dir):
    # Modified version of function from django/core/management/__init__.py.
    command_dir = os.path.join(management_dir, 'commands')
    commands = []
    try:
        for f in os.listdir(command_dir):
            if f.startswith('_'):
                continue
            elif f.endswith('.py') and f[:-3] not in commands:
                commands.append(f[:-3])
            elif f.endswith('.pyc') and f[:-4] not in commands:
                commands.append(f[:-4])
    except OSError:
        pass
    return commands


def prepare_env():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'galaxy.settings.default')
    from django.conf import settings
    if not settings.DEBUG:
        warnings.simplefilter('ignore', DeprecationWarning)
    # import django.utils
    settings.version = __version__
    _fix_mimetypes()


def manage():
    # Prepare the galaxy environment.
    prepare_env()
    # Now run the command (or display the version).
    from django.core.management import execute_from_command_line
    if len(sys.argv) >= 2 and sys.argv[1] in ('version', '--version'):
        sys.stdout.write('galaxy-%s\n' % __version__)
    else:
        execute_from_command_line(sys.argv)


def _fix_mimetypes():
    mimetypes.add_type("image/svg+xml", ".svg", True)
    mimetypes.add_type("image/svg+xml", ".svgz", True)
