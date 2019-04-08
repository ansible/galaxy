# (c) 2012-2019, Ansible
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

from django.test import TestCase

from galaxy.main.models import Collection, CollectionVersion, Namespace


class CollectionModelLatestHighestTest(TestCase):
    '''Test latest and highest version properties for Collection model'''

    def setUp(self):
        namespace = Namespace.objects.create()
        self.collection = Collection.objects.create(namespace=namespace)
        self.v1 = self._add_version('1.1.0')
        self.v2 = self._add_version('2.2.0')

    def tearDown(self):
        CollectionVersion.objects.all().delete()
        Collection.objects.all().delete()
        Namespace.objects.all().delete()

    def _add_version(self, version_to_add):
        return CollectionVersion.objects.create(
                    version=version_to_add,
                    collection=self.collection)

    def test_with_no_addition(self):
        assert(self.collection.latest_version == self.v2)
        assert(self.collection.highest_version == self.v2)

    def test_add_highest_patch(self):
        new_version = self._add_version('2.2.1')
        assert(self.collection.latest_version == new_version)
        assert(self.collection.highest_version == new_version)

    def test_add_highest_minor(self):
        new_version = self._add_version('2.11.0')
        assert(self.collection.latest_version == new_version)
        assert(self.collection.highest_version == new_version)

    def test_add_lower_minor(self):
        new_version = self._add_version('1.2.0')
        assert(self.collection.latest_version == new_version)
        assert(self.collection.highest_version == self.v2)

    def test_add_lower_major(self):
        new_version = self._add_version('0.2.0')
        assert(self.collection.latest_version == new_version)
        assert(self.collection.highest_version == self.v2)

    def test_no_versions(self):
        self.v1.delete()
        self.v2.delete()
        assert(self.collection.latest_version is None)
        assert(self.collection.highest_version is None)

    def test_highest_hidden(self):
        self.v2.hidden = True
        self.v2.save()
        assert(self.collection.latest_version == self.v1)
        assert(self.collection.highest_version == self.v1)

    def test_all_hidden(self):
        self.v1.hidden = True
        self.v2.hidden = True
        self.v1.save()
        self.v2.save()
        assert(self.collection.latest_version is None)
        assert(self.collection.highest_version is None)
