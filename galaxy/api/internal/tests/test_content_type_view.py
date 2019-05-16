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
from rest_framework import status

from galaxy.main import models


class RepoAndCollectionListTest(APITestCase):
    base_url = '/api/internal/ui/type-checker/'

    def setUp(self):
        super().setUp()

        self.namespace = models.Namespace.objects.create(
            name='mynamespace',
        )

        self.provider_ns = models.ProviderNamespace.objects.create(
            provider=models.Provider.objects.get(name__iexact='github'),
            namespace=self.namespace,
        )

        collection = models.Collection.objects.create(
            namespace=self.namespace,
            name='collection'
        )

        models.CollectionVersion.objects.create(
            collection=collection,
            version='1.0.0',
            contents={},
        )

        models.Repository.objects.create(
            name='repo',
            original_name='repo',
            provider_namespace=self.provider_ns
        )

    def test_get_collection(self):
        url = self.base_url + '?namespace=mynamespace&name=collection'
        resp = self.client.get(url).json()
        assert resp['type'] == 'collection'

    def test_get_repo(self):
        url = self.base_url + '?namespace=mynamespace&name=repo'
        resp = self.client.get(url).json()
        assert resp['type'] == 'repository'

    def test_get_bad_params(self):
        error = 'namespace and name parameters are required'

        url = self.base_url + '?namespace=mynamespace'
        resp = self.client.get(url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.json()['message'] == error

        url = self.base_url + '?name=role1'
        resp = self.client.get(url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.json()['message'] == error

        url = self.base_url
        resp = self.client.get(url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.json()['message'] == error

    def test_get_missing_object(self):
        url = self.base_url + '?namespace=mynamespace&name=missing'
        resp = self.client.get(url)

        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()['message'] == \
            "No collection or repository could be found matching " + \
            "the name mynamespace.missing"
