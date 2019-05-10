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

import semantic_version as semver

from galaxy.main.models import Namespace, Collection
from galaxy.worker import exceptions as exc


def _raise_import_fail(msg):
    raise exc.ImportFailed(f'Invalid collection metadata. {msg}') from None


def check_dependencies(collection_info):
    '''Check collection dependencies and matching version are in database'''
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
