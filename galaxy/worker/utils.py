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

from __future__ import absolute_import

import github
import six
import requests

from . import exceptions as exc


def get_readme(token, repo, branch=None):
    """
    Retrieve README from the repo and sanitize by removing all markup.

    Should preserve unicode characters.
    """
    data = {'ref': branch} if branch else {}
    try:
        readme = repo.get_readme(**data)
    except github.UnknownObjectException:
        raise exc.WorkerError("Failed to get README file")
    readme_raw = readme.decoded_content

    if readme.name == 'README.md':
        file_type = 'md'
    elif readme.name == 'README.rst':
        file_type = 'rst'
    else:
        raise exc.WorkerError(
            u'Unable to determine README file type. '
            u'Expected file extensions: ".md", ".rst"')

    headers = {'Authorization': 'token %s' % token,
               'Accept': 'application/vnd.github.VERSION.html'}
    url = "https://api.github.com/repos/%s/readme" % repo.full_name
    response = requests.get(url, headers=headers, data=data)
    response.raise_for_status()
    readme_html = response.text

    return readme_raw, readme_html, file_type


class Context(object):
    def __init__(self, **kwargs):
        for arg, value in six.iteritems(kwargs):
            setattr(self, arg, value)
