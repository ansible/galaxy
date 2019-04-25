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

import semantic_version

from galaxy.main import models
from galaxy.worker import exceptions as exc


def _import_fail(msg):
    raise exc.ImportFailed("Invalid collection metadata. %s" % msg)


def check_dependencies(collection_info):
    '''Check collection dependencies and matching version are in database'''
    dependencies = collection_info.dependencies
    for dep, version_spec in dependencies.items():
        ns_name, name = dep.split('.')

        try:
            ns = models.Namespace.objects.get(name=ns_name)
        except models.Namespace.DoesNotExist:
            _import_fail('Dependency namespace not in galaxy: %s' % dep)
        try:
            collection = models.Collection.objects.get(
                namespace=ns.pk,
                name=name,
            )
        except models.Collection.DoesNotExist:
            _import_fail('Dependency collection not in galaxy: %s' % dep)

        spec = semantic_version.Spec(version_spec)
        versions = models.CollectionVersion.objects.filter(
            collection=collection)
        for v in [item.version for item in versions]:
            try:
                if spec.match(semantic_version.Version(v)):
                    return
            except TypeError:
                # semantic_version Spec('~1') is ok, but match throws error
                pass

        _import_fail('Dependency found in galaxy but no matching '
                     'version found: %s %s' % (dep, version_spec))
