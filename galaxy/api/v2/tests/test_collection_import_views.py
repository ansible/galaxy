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
from pulpcore import constants as pulp_const
from pulpcore.app import models as pulp_models
from rest_framework.test import APITestCase
from rest_framework import status as http_codes

from galaxy.main import models

UserModel = get_user_model()


class TestCollectionImportView(APITestCase):
    url = 'http://testserver/api/v2/collection-imports/{id}/'

    def setUp(self):
        super().setUp()

        self.user = UserModel.objects.create_user(
            username='testuser', password='secret')

        self.namespace = models.Namespace.objects.create(
            pk=12, name='mynamespace')
        self.namespace.owners.set([self.user])

        self.client.login(username=self.user.username, password='secret')

    def test_collection_import_waiting(self):
        pulp_task = pulp_models.Task.objects.create(
            pk=24,
            job_id='0c978c4e-7aba-4a22-be39-de3a433fb687',
            state=pulp_const.TASK_STATES.WAITING,
        )
        models.CollectionImport.objects.create(
            pk=42,
            namespace=self.namespace,
            name='mycollection',
            version='1.2.3',
            pulp_task=pulp_task,
        )
        response = self.client.get(self.url.format(id=42))

        assert response.status_code == http_codes.HTTP_200_OK
        assert response.json() == {
            'id': 42,
            # 'href': '/api/v1/collection-imports/42/',
            'job_id': '0c978c4e-7aba-4a22-be39-de3a433fb687',
            'error': None,
            'started_at': None,
            'finished_at': None,
            'state': 'waiting',
            'namespace': {
                'id': 12,
                'href': 'http://testserver/api/v1/namespaces/12/',
                'name': 'mynamespace',
            },
            'name': 'mycollection',
            'version': '1.2.3',
            'messages': [],
            'lint_records': [],
            'imported_version': None,
        }

    def test_collection_import_complete(self):
        pulp_task = pulp_models.Task.objects.create(
            pk=24,
            job_id='0c978c4e-7aba-4a22-be39-de3a433fb687',
            state=pulp_const.TASK_STATES.COMPLETED,
            started_at='2019-04-09T09:58:02-04:00',
            finished_at='2019-04-09T09:58:59-04:00',
        )
        collection = models.Collection.objects.create(
            pk=25,
            namespace=self.namespace,
            name='mycollection',
        )
        version = models.CollectionVersion.objects.create(
            pk=26,
            collection=collection,
            version='1.2.3',
        )
        models.CollectionImport.objects.create(
            pk=42,
            namespace=self.namespace,
            name='mycollection',
            version='1.2.3',
            pulp_task=pulp_task,
            imported_version=version,
            messages=[
                {
                    'level': 'INFO',
                    'message': 'Task started',
                    'time': 1554818284.0956235,
                },
                {
                    'level': 'INFO',
                    'message': 'Task finished',
                    'time': 1554818305.9033494,
                }
            ],
            lint_records=[
                {
                    'code': 'TEST0001',
                    'type': 'test',
                    'message': 'Test lint record',
                    'severity': 4,
                    'score_type': 'test'
                },
            ]
        )
        response = self.client.get(self.url.format(id=42))

        assert response.status_code == http_codes.HTTP_200_OK
        assert response.json() == {
            'id': 42,
            # 'href': '/api/v1/collection-imports/42/',
            'job_id': '0c978c4e-7aba-4a22-be39-de3a433fb687',
            'error': None,
            'started_at': '2019-04-09T09:58:02-04:00',
            'finished_at': '2019-04-09T09:58:59-04:00',
            'state': 'completed',
            'namespace': {
                'id': 12,
                'href': 'http://testserver/api/v1/namespaces/12/',
                'name': 'mynamespace',
            },
            'name': 'mycollection',
            'version': '1.2.3',
            'lint_records': [
                {
                    'code': 'TEST0001',
                    'message': 'Test lint record',
                    'score_type': 'test',
                    'severity': 4,
                    'type': 'test',
                }
            ],
            'messages': [
                {
                    'level': 'INFO',
                    'message': 'Task started',
                    'time': '2019-04-09T09:58:04.095623-04:00',
                },
                {
                    'level': 'INFO',
                    'message': 'Task finished',
                    'time': '2019-04-09T09:58:25.903349-04:00',
                }
            ],
            'imported_version': {
                'href': 'http://testserver/api/v2/collection-versions/26/',
                'id': 26,
            },
        }

    def test_fail_method_not_allowed(self):
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            response = self.client.generic(method, self.url.format(id=145))
            assert (response.status_code
                    == http_codes.HTTP_405_METHOD_NOT_ALLOWED)
