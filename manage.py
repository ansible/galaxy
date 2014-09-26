#!/usr/bin/env python

#if __name__ == "__main__":
#    local_site_packages = os.path.join(os.path.dirname(__file__), 'main', 'lib', 'site-packages')
#    sys.path.insert(0, local_site_packages)
#
#    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "galaxy.settings")
#
#    from django.core.management import execute_from_command_line
#
#    execute_from_command_line(sys.argv)

# Copyright (c) 2013 AnsibleWorks, Inc.
# All Rights Reserved.

if __name__ == '__main__':
    from galaxy import manage
    manage()

