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
from django.contrib.auth import get_user_model

from galaxy.main import models

UserModel = get_user_model()


class TestCollectionView(APITestCase):

    def setUp(self):
        super().setUp()

        self.owner = UserModel.objects.create_user(
            username='owner', password='secret', email='a@a.com')

        self.imposter = UserModel.objects.create_user(
            username='imposter', password='secret', email='b@a.com')

        self.namespace = models.Namespace.objects.create(
            name='mynamespace',
        )

        self.namespace.owners.set([self.owner, ])

        self.collection = models.Collection.objects.create(
            namespace=self.namespace,
            name='mycollection',
        )
        self.version0 = models.CollectionVersion.objects.create(
            collection=self.collection,
            version='1.0.0',
        )
        self.version1 = models.CollectionVersion.objects.create(
            collection=self.collection,
            version='1.0.1',
        )
        self.collection.latest_version = self.version1
        self.collection.save()

    def test_get_collections(self):
        resp = self.client.get("/api/internal/ui/collections/")
        results = resp.json()['results']

        collection = results[0]

        assert collection['namespace'] == self.namespace.id
        assert collection['name'] == self.collection.name
        assert collection['latest_version']['version'] == self.version1.version

    def test_get_collections2(self):
        resp = self.client.get("/api/internal/ui/collections/")
        results = resp.json()['results']

        collection = results[0]

        assert collection['namespace'] == self.namespace.id
        assert collection['name'] == self.collection.name
        assert collection['latest_version']['version'] == self.version1.version

    def test_get_collection_details(self):
        url = "/api/internal/ui/collections/mynamespace/mycollection/"
        resp = self.client.get(url)

        collection = resp.json()

        assert collection['namespace']['id'] == self.namespace.id
        assert collection['namespace']['name'] == self.namespace.name
        assert collection['name'] == self.collection.name
        assert collection['latest_version']['version'] == self.version1.version
        assert len(collection['all_versions']) == 2

        # We want to make sure that contents aren't returned for all versions
        # because we don't need it and including this would send way too much
        # data over the wire
        assert 'contents' not in collection['all_versions'][0]

    def test_get_collection_details_404(self):
        url = "/api/internal/ui/collections/mynamespace/bogus/"
        resp = self.client.get(url)

        assert resp.status_code == http_codes.HTTP_404_NOT_FOUND
        assert resp.json() == {
            'code': 'not_found',
            'message': 'Not found.',
        }

    def test_deprecate_collection(self):
        self.client.force_authenticate(user=self.owner)
        resp = self.client.put(
            "/api/internal/ui/collections/{}/".format(self.collection.id),
            {
                'id': 89123,
                'name': 'blahBlah',
                'deprecated': True
            },
            format='json'
        )
        data = resp.json()

        # Test deprecation. Verify it is the only writeable field.
        assert data['deprecated'] is True
        assert data['name'] == self.collection.name
        assert data['id'] == self.collection.id

        collection = models.Collection.objects.get(pk=self.collection.id)

        assert collection.deprecated is True

        resp = self.client.put(
            "/api/internal/ui/collections/{}/".format(self.collection.id),
            {
                'deprecated': False
            },
            format='json'
        )

        # Test undeprecating a collection
        assert resp.json()['deprecated'] is False
        collection = models.Collection.objects.get(pk=self.collection.id)
        assert collection.deprecated is False

        # Verify that delete isn't enabled
        resp = self.client.delete(
            "/api/internal/ui/collections/{}/".format(self.collection.id))

        assert resp.status_code == http_codes.HTTP_405_METHOD_NOT_ALLOWED
        assert models.Collection.objects.filter(pk=self.collection.id).exists()

    def test_malicious_deprecate_collection(self):
        resp = self.client.put(
            "/api/internal/ui/collections/{}/".format(self.collection.id),
            {
                'deprecated': True
            },
            format='json'
        )

        # Test unauthenticated users.
        assert resp.json()['code'] == 'permission_denied'
        assert resp.status_code == http_codes.HTTP_403_FORBIDDEN
        collection = models.Collection.objects.get(pk=self.collection.id)
        assert collection.deprecated is False

        self.client.force_authenticate(user=self.imposter)
        resp = self.client.put(
            "/api/internal/ui/collections/{}/".format(self.collection.id),
            {
                'deprecated': True
            },
            format='json'
        )

        # Test authenticated users that aren't owners
        assert resp.json()['code'] == 'permission_denied'
        assert resp.status_code == http_codes.HTTP_403_FORBIDDEN
        collection = models.Collection.objects.get(pk=self.collection.id)
        assert collection.deprecated is False
