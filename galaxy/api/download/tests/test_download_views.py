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

import importlib
from urllib import parse as urlparse
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import override_settings
from pulpcore.app import models as pulp_models
from rest_framework import status as http_codes
from rest_framework.test import APITestCase

from galaxy.main import models


UserModel = get_user_model()


class TestArtifactDownloadView(APITestCase):
    download_url = '/download/{filename}'
    mazer_user_agent = 'Mazer/0.4.0 (linux; python:3.6.8) ansible_galaxy/0.4.0'

    @classmethod
    def setUpClass(cls):
        # Parameters of `storages.backends.s3boto3.S3Boto3Storage` class are
        # initialized as class-attributes on module load.
        # Because `storages.backends.s3boto3` module can be imported even
        # before S3 specific test is executed overriding parameters locally
        # is not effective.
        # Thus we import `storages.backends.s3boto3` module before any
        # request to download view is called.
        super().setUpClass()
        settings = dict(
            AWS_ACCESS_KEY_ID='key',
            AWS_SECRET_ACCESS_KEY='secret',
            AWS_STORAGE_BUCKET_NAME='test',
            AWS_DEFAULT_ACL=None,
        )
        with override_settings(**settings):
            importlib.import_module('storages.backends.s3boto3')

    def setUp(self):
        super().setUp()
        self.sha256 = \
            '01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b'
        self.storage_path = f'artifact/{self.sha256[:2]}/{self.sha256[2:]}'
        self.filename = 'mynamespace-mycollection-1.2.3.tar.gz'

        self.user = UserModel.objects.create_user(
            username='testuser', password='secret')
        self.namespace = models.Namespace.objects.create(name='mynamespace')
        self.namespace.owners.set([self.user])

        self.collection = models.Collection.objects.create(
            namespace=self.namespace, name='mycollection')
        self.version = models.CollectionVersion.objects.create(
            collection=self.collection, version='1.2.3')

    def _create_artifact(self):
        self.artifact = pulp_models.Artifact.objects.create(
            size=427611,
            sha256=self.sha256,
            file=SimpleUploadedFile(self.storage_path, ''),
        )
        self.ca = pulp_models.ContentArtifact.objects.create(
            content=self.version, artifact=self.artifact,
            relative_path=self.filename
        )

    @override_settings(
        MEDIA_ROOT='',
        DEFAULT_FILE_STORAGE='storages.backends.s3boto3.S3Boto3Storage',
        AWS_DEFAULT_ACL=None,
    )
    @mock.patch('storages.backends.s3boto3.S3Boto3Storage.save')
    def test_s3_redirect(self, save_mock):
        save_mock.return_value = self.storage_path
        self._create_artifact()

        old_download_count = self.collection.download_count
        url = self.download_url.format(filename=self.filename)
        response = self.client.get(url, HTTP_USER_AGENT=self.mazer_user_agent)
        assert response.status_code == http_codes.HTTP_302_FOUND

        location = response['Location']
        parsed_url = urlparse.urlparse(location)
        assert parsed_url.scheme == 'https'
        assert parsed_url.netloc == 'test.s3.amazonaws.com'
        assert parsed_url.path == '/' + self.storage_path

        query = urlparse.parse_qs(parsed_url.query)
        assert query['response-content-disposition'] == [
            f'attachment; filename={self.filename}'
        ]

        self.collection.refresh_from_db()
        assert self.collection.download_count == old_download_count + 1

    @override_settings(
        MEDIA_ROOT='/var/lib/galaxy/media/',
        DEFAULT_FILE_STORAGE='pulpcore.app.models.storage.FileSystem',
    )
    def test_direct_serve(self):
        self._create_artifact()
        url = self.download_url.format(filename=self.filename)

        mock_open = mock.mock_open(read_data=b'CONTENT')
        with mock.patch.object(self.artifact.file.storage, 'open', mock_open):
            response = self.client.get(url)

        assert response.status_code == http_codes.HTTP_200_OK
        assert response.getvalue() == b'CONTENT'

    def test_invalid_filename(self):
        filename = 'invalidfilename.tar.gz'
        url = self.download_url.format(filename=filename)
        response = self.client.get(url)

        assert response.status_code == http_codes.HTTP_404_NOT_FOUND
        assert response.json() == {
            'code': 'not_found',
            'message': f'Artifact "{filename}" does not exist.',
        }

    def test_not_found(self):
        filename = 'wrongnamespace-mycollection-1.2.3.tar.gz'
        url = self.download_url.format(filename=filename)
        response = self.client.get(url)

        assert response.status_code == http_codes.HTTP_404_NOT_FOUND
        assert response.json() == {
            'code': 'not_found',
            'message': f'Artifact "{filename}" does not exist.',
        }
