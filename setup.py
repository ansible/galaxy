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

import os
import datetime
import glob
import sys

from distutils import log
from setuptools import setup
from setuptools.command.sdist import sdist as _sdist


from galaxy import __version__

build_timestamp = os.getenv(
    "BUILD", datetime.datetime.now().strftime('-%Y%m%d%H%M'))

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


class sdist_galaxy(_sdist, object):
    '''
    Custom sdist command to distribute some files as .pyc only.
    '''

    def make_release_tree(self, base_dir, files):
        for f in files[:]:
            if f.endswith('.egg-info/SOURCES.txt'):
                files.remove(f)
                sources_txt_path = f
        super(sdist_galaxy, self).make_release_tree(base_dir, files)
        new_sources_path = os.path.join(base_dir, sources_txt_path)
        if os.path.isfile(new_sources_path):
            log.warn('unlinking previous %s', new_sources_path)
            os.unlink(new_sources_path)
        log.info('writing new %s', new_sources_path)
        new_sources = file(new_sources_path, 'w')
        for line in file(sources_txt_path, 'r'):
            line = line.strip()
            if line in self.pyc_only_files:
                line = line + 'c'
            new_sources.write(line + '\n')

    def make_distribution(self):
        self.pyc_only_files = []
        import py_compile
        for n, f in enumerate(self.filelist.files[:]):
            if not f.startswith('galaxy/'):
                continue
            if f.startswith('galaxy/lib/site-packages'):
                continue
            if f.startswith('galaxy/scripts'):
                continue
            if f.startswith('galaxy/plugins'):
                continue
            if f.find('migrations/'):
                continue
            if f.endswith('.py'):
                log.info('using pyc for: %s', f)
                py_compile.compile(f, doraise=True)
                self.filelist.files[n] = f + 'c'
                self.pyc_only_files.append(f)
        super(sdist_galaxy, self).make_distribution()


setup(
    name='galaxy',
    version=__version__.split("-")[0],  # FIXME: Should keep full version here?
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
    options={
        'egg_info': {
            'tag_build': '-%s' % build_timestamp,
        },
        'aliases': {
            'dev_build': 'clean --all egg_info sdist_galaxy',
            'release_build': 'clean --all egg_info -b "" sdist_galaxy',
        },
    },
    cmdclass={
        'sdist_galaxy': sdist_galaxy,
    },
)
