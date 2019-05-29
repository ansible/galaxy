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

from django.contrib.auth import get_user_model
from pulpcore.app import models as pulp_models
from rest_framework import status as http_codes
from rest_framework.test import APITestCase

from galaxy.main import models


UserModel = get_user_model()

mazer_user_agent = 'Mazer/0.4.0 (linux; python:3.6.8) ansible_galaxy/0.4.0'


class TestCollectionArtifactView(APITestCase):

    def setUp(self):
        super().setUp()

        self.user = UserModel.objects.create_user(
            username='testuser', password='secret')
        self.namespace = models.Namespace.objects.create(name='mynamespace')
        self.namespace.owners.set([self.user])

        self.collection = models.Collection.objects.create(
            namespace=self.namespace, name='mycollection')
        self.version = models.CollectionVersion.objects.create(
            collection=self.collection, version='1.2.3')
        self.artifact = pulp_models.Artifact.objects.create(
            size=427611,
            sha256='01ba4719c80b6fe911b091a7c05124b6'
                   '4eeece964e09c058ef8f9805daca546b'
        )
        self.ca = pulp_models.ContentArtifact.objects.create(
            content=self.version, artifact=self.artifact,
            relative_path='mynamespace-mycollection-1.2.3.tar.gz')

    def test_get_by_id(self):
        response = self.client.get(
            f'/api/v2/collection-versions/{self.version.pk}/artifact/')

        assert response.status_code == http_codes.HTTP_200_OK
        assert response.json() == {
            'filename': 'mynamespace-mycollection-1.2.3.tar.gz',
            'size': 427611,
            'sha256': self.artifact.sha256,
            'download_url': 'http://testserver/download'
                            '/mynamespace-mycollection-1.2.3.tar.gz',
        }

    def test_get_by_name(self):
        response = self.client.get(
            '/api/v2/collections/mynamespace/mycollection'
            '/versions/1.2.3/artifact/')

        assert response.status_code == http_codes.HTTP_200_OK
        assert response.json() == {
            'filename': 'mynamespace-mycollection-1.2.3.tar.gz',
            'size': 427611,
            'sha256': self.artifact.sha256,
            'download_url': 'http://testserver/download'
                            '/mynamespace-mycollection-1.2.3.tar.gz',
        }

    def test_get_by_id_not_found(self):
        pk = self.version.pk + 1
        response = self.client.get(
            f'/api/v2/collection-versions/{pk}/artifact/')
        assert response.status_code == http_codes.HTTP_404_NOT_FOUND

    def test_get_by_name_not_found(self):
        response = self.client.get(
            '/api/v2/collections/mynamespace/mycollection'
            '/versions/1.2.4/artifact/')
        assert response.status_code == http_codes.HTTP_404_NOT_FOUND

    def test_fail_method_not_allowed(self):
        url = '/api/v2/collection-versions/{pk}/artifact/'
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            response = self.client.generic(method, url.format(pk=42))
            assert (response.status_code
                    == http_codes.HTTP_405_METHOD_NOT_ALLOWED)


class TestVersionDetailView(APITestCase):
    url_id = '/api/v2/collection-versions/{pk}/'
    url_version = '/api/v2/collections/{ns}/{name}/versions/{version}/'

    def setUp(self):
        super().setUp()
        self.namespace = models.Namespace.objects.create(
            name='mynamespace')
        self.collection = models.Collection.objects.create(
            namespace=self.namespace,
            name='mycollection')
        self.version = models.CollectionVersion.objects.create(
            collection=self.collection,
            version='1.0.0',
            metadata={
                'name': self.collection.name,
                'version': '1.0.0',
            },
        )
        self.artifact = pulp_models.Artifact.objects.create(
            size=427611,
            sha256='01ba4719c80b6fe911b091a7c05124b6'
                   '4eeece964e09c058ef8f9805daca546b'
        )
        self.ca = pulp_models.ContentArtifact.objects.create(
            content=self.version, artifact=self.artifact,
            relative_path='mynamespace-mycollection-1.0.0.tar.gz')

    def test_get_by_id(self):
        url = self.url_id.format(pk=self.version.pk)

        response = self.client.get(url)
        self._assert_response_valid(response)

    def test_get_by_name(self):
        url = self.url_version.format(
            ns=self.namespace.name,
            name=self.collection.name,
            version=self.version.version,
        )

        response = self.client.get(url)
        self._assert_response_valid(response)

    def _assert_response_valid(self, response):
        assert response.status_code == http_codes.HTTP_200_OK
        assert response.json() == {
            'id': self.version.pk,
            'href': 'http://testserver/api/v2/collections/mynamespace'
                    '/mycollection/versions/1.0.0/',
            'download_url': 'http://testserver/download/'
                            'mynamespace-mycollection-1.0.0.tar.gz',
            'namespace': {
                'id': self.namespace.pk,
                'name': 'mynamespace',
                'href': f'http://testserver/api/v1'
                        f'/namespaces/{self.namespace.pk}/',
            },
            'collection': {
                'id': self.collection.pk,
                'name': 'mycollection',
                'href': 'http://testserver/api/v2/collections'
                        '/mynamespace/mycollection/',
            },
            'version': '1.0.0',
            'hidden': False,
            'metadata': {
                'name': 'mycollection', 'version': '1.0.0'
            }
        }

    def test_view_404(self):
        response = self.client.get(self.url_id.format(pk=self.version.pk + 1))
        assert response.status_code == http_codes.HTTP_404_NOT_FOUND


class TestVersionListView(APITestCase):
    url_id = '/api/v2/collections/{pk}/versions/'
    url_name = '/api/v2/collections/{ns}/{name}/versions/'

    def setUp(self):
        super().setUp()
        self.namespace = models.Namespace.objects.create(
            name='mynamespace')
        self.collection = models.Collection.objects.create(
            namespace=self.namespace,
            name='mycollection')
        self.version1 = models.CollectionVersion.objects.create(
            collection=self.collection, version='1.0.0')
        self.version2 = models.CollectionVersion.objects.create(
            collection=self.collection, version='2.2.1')
        self.version3 = models.CollectionVersion.objects.create(
            collection=self.collection, version='2.12.2')
        self.version4 = models.CollectionVersion.objects.create(
            collection=self.collection, version='2.2.2')
        self.version5 = models.CollectionVersion.objects.create(
            collection=self.collection, version='0.3.0')

    def test_view_success(self):
        urls = [
            self.url_id.format(pk=self.collection.pk),
            self.url_name.format(
                ns=self.namespace.name,
                name=self.collection.name,
            ),
        ]

        for url in urls:
            response = self.client.get(url)
            assert response.status_code == http_codes.HTTP_200_OK
            results = response.json()['results']
            assert results[0]['version'] == self.version3.version
            assert results[1]['version'] == self.version4.version
            assert results[2]['version'] == self.version2.version
            assert results[3]['version'] == self.version1.version
            assert results[4]['version'] == self.version5.version

    def test_view_404(self):
        response = self.client.get(
            self.url_id.format(pk=self.collection.pk + 1))
        assert response.status_code == http_codes.HTTP_404_NOT_FOUND
