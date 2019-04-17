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

from rest_framework.test import APITestCase
from rest_framework import status as http_codes

from galaxy.main import models


class CollectionViewTests(APITestCase):

    def setUp(self):
        super().setUp()
        self.namespace = models.Namespace.objects.create(
            name='mynamespace',
        )
        self.collection = models.Collection.objects.create(
            namespace=self.namespace,
            name='mycollection',
        )
        self.version0 = models.CollectionVersion.objects.create(
            collection=self.collection,
            version='1.0.0',
            contents='{}',
        )
        self.version = models.CollectionVersion.objects.create(
            collection=self.collection,
            version='1.0.1',
            contents='{}',
        )

    def test_get_collections(self):
        resp = self.client.get("/api/internal/ui/collections/")
        results = resp.json()['results']

        collection = results[0]

        assert collection['namespace'] == self.namespace.id
        assert collection['name'] == self.collection.name
        assert collection['latest_version']['version'] == self.version.version

    def test_get_collections2(self):
        resp = self.client.get("/api/internal/ui/collections/")
        results = resp.json()['results']

        collection = results[0]

        assert collection['namespace'] == self.namespace.id
        assert collection['name'] == self.collection.name
        assert collection['latest_version']['version'] == self.version.version

    def test_get_collection_details(self):
        url = "/api/internal/ui/collections/mynamespace/mycollection/"
        resp = self.client.get(url)

        collection = resp.json()

        assert collection['namespace']['id'] == self.namespace.id
        assert collection['namespace']['name'] == self.namespace.name
        assert collection['name'] == self.collection.name
        assert collection['latest_version']['version'] == self.version.version
        assert len(collection['all_versions']) == 2

        # We want to make sure that contents aren't returned for all versions
        # because we don't need it and including this would send way too much
        # data over the wire
        assert 'contents' not in collection['all_versions'][0]

    def test_get_collection_details_404(self):
        url = "/api/internal/ui/collections/mynamespace/bogus/"
        resp = self.client.get(url)

        collection = resp.json()

        assert collection['detail'] == "Not found."
        assert resp.status_code == http_codes.HTTP_404_NOT_FOUND
