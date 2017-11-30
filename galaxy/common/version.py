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

    :return str: Package version string
    :raises subprocess.CalledProcessError: If `git` command failed.
    """
    tag_info = subprocess.check_output([
        'git', 'describe', '--match', TAG_PREFIX + '*']
    ).strip().lstrip(TAG_PREFIX)
    chunks = tag_info.rsplit('-', 2)

    if len(chunks) == 1:
        return chunks[0]

    return '{0}.dev{1}+{2}'.format(*chunks)
