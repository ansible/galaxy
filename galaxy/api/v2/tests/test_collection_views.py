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
import hashlib
from unittest import mock

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status as http_codes

from galaxy.main import models

UserModel = get_user_model()


class TestCollectionListView(APITestCase):

    url = 'http://testserver/api/v2/collections/'

    def setUp(self):
        super().setUp()

        self.user = UserModel.objects.create_user(
            username='testuser', password='secret')

        self.namespace = models.Namespace.objects.create(name='mynamespace')
        self.namespace.owners.set([self.user])

        self.client.login(username=self.user.username, password='secret')

        patcher = mock.patch('galaxy.common.tasking.create_task')
        self.create_task_mock = patcher.start()
        self.addCleanup(patcher.stop)

    def test_upload(self):
        task_obj = models.ImportTask(id=42)
        self.create_task_mock.return_value = task_obj

        open_mock = mock.mock_open(read_data=b'Test data')
        with open_mock() as fp:
            fp.name = 'mynamespace-mycollection-1.2.3.tar.gz'
            response = self.client.post(self.url, data={
                'file': fp
            })

        self.create_task_mock.assert_called_once()
        assert response.status_code == http_codes.HTTP_202_ACCEPTED
        assert response.json() == {
            'task': 'http://testserver/api/v2/collection-imports/42/'}

    def test_upload_w_sha(self):
        task_obj = models.ImportTask(id=42)
        self.create_task_mock.return_value = task_obj

        file_data = b'Test data'
        file_sha256 = hashlib.sha256(file_data).hexdigest()

        open_mock = mock.mock_open(read_data=file_data)
        with open_mock() as fp:
            fp.name = 'mynamespace-mycollection-1.2.3.tar.gz'
            response = self.client.post(self.url, data={
                'file': fp,
                'sha256': file_sha256,
            })

        assert response.status_code == http_codes.HTTP_202_ACCEPTED
        assert response.json() == {
            'task': 'http://testserver/api/v2/collection-imports/42/'}
        self.create_task_mock.assert_called_once()

    def test_upload_w_invalid_sha(self):
        file_data = b'Test data'
        file_sha256 = hashlib.sha256(file_data + b'x').hexdigest

        open_mock = mock.mock_open(read_data=file_data)
        with open_mock() as fp:
            fp.name = 'mynamespace-mycollection-1.2.3.tar.gz'
            response = self.client.post(self.url, data={
                'file': fp,
                'sha256': file_sha256,
            })

        assert response.status_code == http_codes.HTTP_400_BAD_REQUEST
        assert response.json() == {
            'code': 'invalid',
            'message': 'The sha256 checksum did not match.'
        }

    def test_upload_invalid_namespace(self):
        open_mock = mock.mock_open(read_data='Test data')
        with open_mock() as fp:
            fp.name = 'wrongnamespace-mycollection-1.2.3.tar.gz'
            response = self.client.post(self.url, data={
                'file': fp,
            })

        assert response.status_code == http_codes.HTTP_400_BAD_REQUEST
        assert response.json() == {
            'code': 'invalid',
            'message': 'Namespace "wrongnamespace" does not exist.'
        }

    def test_upload_version_conflict(self):
        collection = models.Collection.objects.create(
            namespace=self.namespace, name='mycollection')
        models.CollectionVersion.objects.create(
            collection=collection, version='1.2.3')

        open_mock = mock.mock_open(read_data=b'Test data')
        with open_mock() as fp:
            fp.name = 'mynamespace-mycollection-1.2.3.tar.gz'
            response = self.client.post(self.url, data={
                'file': fp
            })

        assert response.status_code == http_codes.HTTP_409_CONFLICT
        assert response.json() == {
            'code': 'conflict.collection_exists',
            'message': 'Collection "mynamespace-mycollection-1.2.3"'
                       ' already exists.'
        }

    def test_fail_method_not_allowed(self):
        for method in ['GET', 'PUT', 'PATCH', 'DELETE']:
            response = self.client.generic(method, self.url)
            assert (response.status_code
                    == http_codes.HTTP_405_METHOD_NOT_ALLOWED)


class TestCollectionDetailView(APITestCase):
    url_id = 'http://testserver/api/v2/collections/{pk}/'
    url_name = 'http://testserver/api/v2/collections/{ns}/{name}/'

    def setUp(self):
        super().setUp()
        self.namespace = models.Namespace.objects.create(
            name='mynamespace')
        self.collection = models.Collection.objects.create(
            namespace=self.namespace,
            name='mycollection')
        self.version1 = models.CollectionVersion.objects.create(
            collection=self.collection, version='1.1.2')
        self.version2 = models.CollectionVersion.objects.create(
            collection=self.collection, version='1.1.12')
        self.version3 = models.CollectionVersion.objects.create(
            collection=self.collection, version='1.0.1')

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
            result = response.json()
            assert result['id'] == self.collection.pk
            assert result['href'] == urls[1]
            assert result['name'] == self.collection.name
            assert result['namespace']['name'] == self.namespace.name
            assert result['versions_url'] == urls[1] + 'versions/'
            assert (result['highest_version']['version'] ==
                    self.version2.version)
            assert result['deprecated'] is False

    def test_view_404(self):
        response = self.client.get(self.url_id.format(pk=self.collection.pk+1))
        assert response.status_code == http_codes.HTTP_404_NOT_FOUND
