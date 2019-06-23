# (c) 2012-2019, Ansible by Red Hat
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

import json

from galaxy.main.models import Platform


class _ContentJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for galaxy.importer.models.Content objects."""
    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            pass

        if isinstance(obj, Platform):
            return {'name': obj.name.lower(),
                    'release': obj.release.lower()}

        try:
            return obj.name.lower()
        except AttributeError:
            return str(obj).lower()


def serialize_contents(content_list):
    """Serialize content objects with nested data into json.

    :param content_list: list of galaxy.importer.models.Content
    :return: list of nested dictionaries with content data
    """

    serialized_contents = []
    for content in content_list:
        data = json.dumps(content.__dict__, cls=_ContentJSONEncoder)
        serialized_contents.append(json.loads(data))

    return serialized_contents


def get_subset_contents(content_list):
    """Return subset of content fields for storage in a collection.

    :param content_list: list of dictionaries with content data
    :return: list of dictionaries with content data
    """

    content_keys = ['name', 'content_type', 'description',
                    'scores', 'metadata', 'role_meta']
    role_meta_keys = ['author', 'company', 'license',
                      'min_ansible_version', 'dependencies',
                      'tags', 'platforms', 'cloud_platforms']

    content_list_subset = []
    for content in content_list:
        data = {k: content.get(k, None) for k in content_keys}
        if data['role_meta']:
            role_meta = data.pop('role_meta')
            data['role_meta'] = {k: role_meta.get(k, None)
                                 for k in role_meta_keys}
        content_list_subset.append(data)
    return content_list_subset
