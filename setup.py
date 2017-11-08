#!/usr/bin/env python
# (c) 2012-2016, Ansible by Red Hat
#
#  This file is part of Ansible Galaxy
#
#  Ansible Galaxy is free software: you can redistribute it and/or modify
#  it under the terms of the Apache License as published by
#  the Apache Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  Ansible Galaxy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  Apache License for more details.
#
#  You should have received a copy of the Apache License
#  along with Galaxy.  If not, see <http://www.apache.org/licenses/>.

import glob
import os
import sys

from setuptools import setup

from galaxy.common import version

# Paths we'll use later
etcpath = "/etc/galaxy"
homedir = "/var/lib/galaxy"
if os.path.exists("/etc/debian_version"):
    webconfig = "/etc/apache2/conf.d"
else:
    webconfig = "/etc/httpd/conf.d"

if (os.environ.get('USER', '') == 'vagrant'
        or os.environ.get('SUDO_USER', '') == 'vagrant'):
    del os.link

#####################################################################
# Helper Functions


def explode_glob_path(path):
    """Take a glob and hand back the full recursive expansion,
    ignoring links.
    """

    result = []
    includes = glob.glob(path)
    for item in includes:
        if os.path.isdir(item) and not os.path.islink(item):
            result.extend(explode_glob_path(os.path.join(item, "*")))
        else:
            result.append(item)
    return result


def proc_data_files(data_files):
    """Because data_files doesn't natively support globs...
    let's add them.
    """

    result = []

    # If running in a virtualenv, don't return data files that would install to
    # system paths (mainly useful for running tests via tox).
    if hasattr(sys, 'real_prefix'):
        return result

    for dir, files in data_files:
        includes = []
        for item in files:
            includes.extend(explode_glob_path(item))
        result.append((dir, includes))
    return result

#####################################################################


setup(
    name='galaxy',
    version=version.get_git_version(),
    author='Ansible, Inc.',
    author_email='support@ansible.com',
    description='Galaxy: Find, reuse and share the best Ansible content.',
    long_description='Galaxy is a web site and command line tool for '
                     'creating and sharing Ansible roles.',
    license='Apache-2.0',
    keywords='ansible galaxy',
    url='http://github.com/ansible/galaxy',
    packages=['galaxy'],
    include_package_data=True,
    zip_safe=False,
    setup_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators'
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
    ],
    entry_points={
        'console_scripts': ['galaxy-manage = galaxy:manage'],
    },
    data_files=proc_data_files([
        ("%s" % homedir, ["config/wsgi.py",
                          "galaxy/static/favicon.ico"])]
    ),
)
