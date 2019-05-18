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


class TestRepoAndCollectionList(APITestCase):
    base_url = '/api/internal/ui/repos-and-collections/'

    def setUp(self):
        super().setUp()

        self.namespace = models.Namespace.objects.create(
            name='mynamespace',
        )

        self.provider_ns = models.ProviderNamespace.objects.create(
            provider=models.Provider.objects.get(name__iexact='github'),
            namespace=self.namespace,
        )

        self.num_collections = 18
        self.num_repositories = 25

        for x in range(self.num_collections):
            collection = models.Collection.objects.create(
                namespace=self.namespace,
                name='Collection' + str(x),
            )

            models.CollectionVersion.objects.create(
                collection=collection,
                version='1.0.0',
                contents={},
            )

        for x in range(self.num_repositories):
            name = 'Repository' + str(x)
            models.Repository.objects.create(
                name=name,
                original_name=name,
                provider_namespace=self.provider_ns
            )

        # Load a sorted reference list of repos and collections. Since the API
        # sorts results by name, these lists should match the ordering from
        # the API and can be used to verify that the API is returning the
        # correct range of results for a given query.
        self.collections = list(models.Collection.objects.filter(
            namespace=self.namespace).order_by('name'))
        self.repos = list(models.Repository.objects.filter(
            provider_namespace__namespace=self.namespace).order_by('name'))

    def test_get_page_1(self):
        url = self.base_url + '?namespace=mynamespace'
        resp = self.client.get(url).json()

        assert len(resp['collection']['results']) == 10
        assert resp['collection']['count'] == self.num_collections
        assert resp['collection']['results'][0]['name'] == \
            self.collections[0].name
        assert resp['collection']['results'][9]['name'] == \
            self.collections[9].name

        assert len(resp['repository']['results']) == 0
        assert resp['repository']['count'] == self.num_repositories

    def test_get_page_2(self):
        url = self.base_url + '?namespace=mynamespace&page=2'
        resp = self.client.get(url).json()

        assert len(resp['collection']['results']) == 8
        assert resp['collection']['count'] == self.num_collections
        assert resp['collection']['results'][0]['name'] == \
            self.collections[10].name
        assert resp['collection']['results'][7]['name'] == \
            self.collections[17].name

        assert len(resp['repository']['results']) == 2
        assert resp['repository']['count'] == self.num_repositories
        assert resp['repository']['results'][0]['name'] == self.repos[0].name
        assert resp['repository']['results'][1]['name'] == self.repos[1].name

    def test_get_page_3(self):
        url = self.base_url + '?namespace=mynamespace&page=3'
        resp = self.client.get(url).json()

        assert len(resp['collection']['results']) == 0
        assert resp['collection']['count'] == self.num_collections

        assert len(resp['repository']['results']) == 10
        assert resp['repository']['count'] == self.num_repositories
        assert resp['repository']['results'][0]['name'] == self.repos[2].name
        assert resp['repository']['results'][9]['name'] == self.repos[11].name

    def test_get_collections(self):
        url = self.base_url + '?namespace=mynamespace&type=collection&page=2'
        resp = self.client.get(url).json()

        assert len(resp['collection']['results']) == 8
        assert resp['collection']['count'] == self.num_collections
        assert resp['collection']['results'][0]['name'] == \
            self.collections[10].name
        assert resp['collection']['results'][7]['name'] == \
            self.collections[17].name

        assert len(resp['repository']['results']) == 0
        assert resp['repository']['count'] == 0

    def test_get_repositories(self):
        url = self.base_url + '?namespace=mynamespace&type=repository'
        resp = self.client.get(url).json()

        assert len(resp['collection']['results']) == 0
        assert resp['collection']['count'] == 0

        assert len(resp['repository']['results']) == 10
        assert resp['repository']['count'] == self.num_repositories
        assert resp['repository']['results'][0]['name'] == self.repos[0].name
        assert resp['repository']['results'][9]['name'] == self.repos[9].name

    def test_get_page_size_20(self):
        url = self.base_url + '?namespace=mynamespace&page_size=20'
        resp = self.client.get(url).json()

        assert len(resp['collection']['results']) == self.num_collections
        assert resp['collection']['count'] == 18
        assert resp['collection']['results'][0]['name'] == \
            self.collections[0].name
        assert resp['collection']['results'][17]['name'] == \
            self.collections[17].name

        assert len(resp['repository']['results']) == 2
        assert resp['repository']['count'] == self.num_repositories
        assert resp['repository']['results'][0]['name'] == self.repos[0].name
        assert resp['repository']['results'][1]['name'] == self.repos[1].name

    def test_get_filter_name(self):
        url = self.base_url + '?namespace=mynamespace&name=repository'
        resp = self.client.get(url).json()

        assert len(resp['collection']['results']) == 0
        assert resp['collection']['count'] == 0

        assert len(resp['repository']['results']) == 10
        assert resp['repository']['count'] == self.num_repositories
        assert resp['repository']['results'][0]['name'] == self.repos[0].name
        assert resp['repository']['results'][9]['name'] == self.repos[9].name

    def test_namespace_missing(self):
        url = self.base_url
        resp = self.client.get(url)

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.json()['message'] == 'The namespace parameter is required'

    def test_bad_pagination(self):
        url = self.base_url + '?namespace=mynamespace&page=One'
        resp = self.client.get(url)

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.json()['message'] == 'Pagination values must be numbers'

    def test_bad_order(self):
        url = self.base_url + '?namespace=mynamespace&order=66'
        resp = self.client.get(url)

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert 'download_count' in resp.json()['message']
        assert 'name' in resp.json()['message']
