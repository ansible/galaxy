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

import os.path
import sys
import warnings

__version__ = '2.2.0'
__all__ = ['__version__']


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
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'galaxy.settings')
    local_site_packages = os.path.join(os.path.dirname(__file__), 'lib', 'site-packages')
    sys.path.insert(0, local_site_packages)
    from django.conf import settings
    if not settings.DEBUG:
        warnings.simplefilter('ignore', DeprecationWarning)
    # import django.utils
    settings.version = __version__


def manage():
    # Prepare the galaxy environment.
    prepare_env()
    # Now run the command (or display the version).
    from django.core.management import execute_from_command_line
    if len(sys.argv) >= 2 and sys.argv[1] in ('version', '--version'):
        sys.stdout.write('galaxy-%s\n' % __version__)
    else:
        execute_from_command_line(sys.argv)
