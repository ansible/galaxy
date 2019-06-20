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

import semantic_version as semver

from galaxy.main.models import Namespace, Collection, Platform
from galaxy.worker import exceptions as exc


def _raise_import_fail(msg):
    raise exc.ImportFailed(f'Invalid collection metadata. {msg}') from None


def check_dependencies(collection_info):
    """Check collection dependencies and matching version are in database."""
    dependencies = collection_info.dependencies
    for dep, version_spec in dependencies.items():
        ns_name, name = dep.split('.')

        try:
            ns = Namespace.objects.get(name=ns_name)
        except Namespace.DoesNotExist:
            _raise_import_fail(f'Dependency namespace not in galaxy: {dep}')
        try:
            collection = Collection.objects.get(namespace=ns.pk, name=name)
        except Collection.DoesNotExist:
            _raise_import_fail(f'Dependency collection not in galaxy: {dep}')

        spec = semver.Spec(version_spec)
        versions = (
            semver.Version(v.version) for v in collection.versions.all())
        no_match_message = ('Dependency found in galaxy but no matching '
                            f'version found: {dep} {version_spec}')
        try:
            if not spec.select(versions):
                _raise_import_fail(no_match_message)
        except TypeError:
            # semantic_version allows a Spec('~1') but throws TypeError on
            # attempted match to it
            _raise_import_fail(no_match_message)


def get_quality_score(contents_json):
    '''Calculate collection quality score from content scores.'''
    coll_points = 0.0
    count = 0
    for content in contents_json:
        if content['scores']:
            coll_points += content['scores']['quality']
            count += 1
    quality_score = None if count == 0 else coll_points / count
    return quality_score


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
