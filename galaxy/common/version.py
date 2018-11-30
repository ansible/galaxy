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
from __future__ import unicode_literals

import subprocess

TAG_PREFIX = 'v'


def get_package_version(package):
    """
    Returns package version from installaed package metadata, otherwise
    generates it based on git version tag.

    :param str package: Package name
    :return str: Package version string
    """
    import pkg_resources
    try:
        dist = pkg_resources.get_distribution(package)
        return dist.version
    except pkg_resources.DistributionNotFound:
        return get_git_version()


def get_git_version():
    """
    Returns package version in PEP440 format based on latest annotated
    version tag. Version tags should have prefix 'v'.

    :return str: A version string.
    :raises RuntimeError: If cannot determine git version string.
    """
    try:
        # TODO(cutwater): Replace `.decode('utf-8')` call with subprocess
        # parameter `encoding` after dropping Python 2.7 support.
        tag_info = subprocess.check_output([
            'git', 'describe', '--always', '--match', TAG_PREFIX + '*']
        ).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        raise RuntimeError('Cannot determine git version string.')

    if '-' in tag_info:
        chunks = tag_info.lstrip(TAG_PREFIX).rsplit('-', 2)
        return '{0}.dev{1}+{2}'.format(*chunks)

    if '.' in tag_info:
        return tag_info.lstrip(TAG_PREFIX)

    return '0.0.0.dev0+{0}'.format(tag_info)


def get_version_name():
    """
    Returns the version name. Minor releases for 3.0.0 will be named after
    Daft Punk songs.
    """

    return "Doin' it Right"


def get_team_members():
    """
    Returns list of team members who have worked on Ansible Galaxy
    """
    members = [
        "chouseknecht",
        "cutwater",
        "alikins",
        "newswangerd",
        "awcrosby",
        "tima",
        "gregdek"
    ]

    return members
