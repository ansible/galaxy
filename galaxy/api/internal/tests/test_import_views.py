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

import datetime as dt

from django.contrib.auth import get_user_model
from django.utils import timezone
from pulpcore import constants as pulp_const
from pulpcore.app import models as pulp_models
from rest_framework.test import APITestCase
from rest_framework import status as http_codes

from galaxy.main import models
from galaxy import constants as const

UserModel = get_user_model()


class NamespaceImportsList(APITestCase):
    url = '/api/internal/ui/namespaces/{ns}/imports/'

    def setUp(self):
        super().setUp()

        self.user = UserModel.objects.create_user(
            username='testuser', password='secret')

        self.namespace = self._create_namespace('myns')
        self.provider_ns = models.ProviderNamespace.objects.create(
            provider=models.Provider.objects.get(name__iexact='github'),
            namespace=self.namespace,
        )
        self.repos = [
            self._create_repo('myrepo1'),
            self._create_repo('myrepo2'),
        ]

        now = timezone.now()
        start = now - dt.timedelta(hours=10)

        self.repo_imports = [
            self._create_repo_import(
                repository=self.repos[0],
                state=const.ImportTaskState.SUCCESS,
                started_at=start + dt.timedelta(hours=4),
                finished_at=now,

            ),
            self._create_repo_import(
                repository=self.repos[1],
                state=const.ImportTaskState.PENDING,
                started_at=start + dt.timedelta(hours=2),
            ),
        ]

        self.collection_imports = [
            self._create_collection_import(
                state=pulp_const.TASK_STATES.WAITING,
                name='mycollection1',
                version='0.9.9',
                started_at=start + dt.timedelta(hours=3),
            ),
            self._create_collection_import(
                state=pulp_const.TASK_STATES.COMPLETED,
                name='mycollection2',
                version='1.0.1',
                started_at=start + dt.timedelta(hours=1),
                finished_at=now,
            )
        ]

    def _create_namespace(self, name):
        ns = models.Namespace.objects.create(name=name)
        ns.owners.set([self.user])
        return ns

    def _create_repo(self, name):
        repo = models.Repository.objects.create(
            name=name, original_name=name, provider_namespace=self.provider_ns)
        repo.owners.set([self.user])
        return repo

    def _create_repo_import(
            self, *, repository, state, started_at=None, finished_at=None):
        return models.ImportTask.objects.create(
            repository=repository,
            state=state,
            owner=self.user,
            started=started_at,
            finished=finished_at,
        )

    def _create_collection_import(
            self, *, state, name, version, started_at=None, finished_at=None):
        pulp_task = pulp_models.Task.objects.create(
            state=state,
            started_at=started_at,
            finished_at=finished_at,
        )
        return models.CollectionImport.objects.create(
            name=name,
            version=version,
            namespace=self.namespace,
            pulp_task=pulp_task,
        )

    def test_list_all(self):
        response = self.client.get(self.url.format(ns=self.namespace.id))
        assert response.status_code == http_codes.HTTP_200_OK

        data = response.json()
        assert data['count'] == 4

        results = data['results']
        assert len(results) == 4

        ns = self.namespace
        task = self.repo_imports[0]
        assert results[0] == {
            'id': task.id,
            'type': 'repository',
            'href': 'http://testserver/api/v1/imports/{}/'.format(task.id),
            'name': 'myrepo1',
            'namespace': {
                'id': self.namespace.id,
                'href': 'http://testserver/api/v1/'
                        'namespaces/{}/'.format(ns.id),
                'name': self.namespace.name,
            },
            'state': 'completed',
            'started_at': timezone.localtime(
                self.repo_imports[0].started).isoformat(),
            'finished_at': timezone.localtime(
                self.repo_imports[0].finished).isoformat(),
        }

        task = self.collection_imports[0]
        assert results[1] == {
            'id': task.id,
            'type': 'collection',
            'href': ('http://testserver/api/v2/'
                     'collection-imports/{}/'.format(task.id)),
            'name': 'mycollection1',
            'version': '0.9.9',
            'namespace': {
                'id': self.namespace.id,
                'href': 'http://testserver/api/v1/'
                        'namespaces/{}/'.format(ns.id),
                'name': self.namespace.name,
            },
            'state': 'waiting',
            'started_at': timezone.localtime(task.started_at).isoformat(),
            'finished_at': None,
        }

        self.assertDictContainsSubset({
            'name': 'myrepo2',
            'type': 'repository',
            'state': 'waiting',
        }, results[2])

        self.assertDictContainsSubset({
            'name': 'mycollection2',
            'type': 'collection',
            'state': 'completed',
        }, results[3])

    def test_list_filter_by_type(self):
        response = self.client.get(self.url.format(ns=self.namespace.id),
                                   data={'type': 'collection'})
        assert response.status_code == http_codes.HTTP_200_OK

        data = response.json()
        assert data['count'] == 2

        results = data['results']
        assert len(results) == 2

        self.assertDictContainsSubset({
            'name': 'mycollection1',
            'type': 'collection',
        }, results[0])
        self.assertDictContainsSubset({
            'name': 'mycollection2',
            'type': 'collection',
        }, results[1])

    def test_list_filter_by_name(self):
        response = self.client.get(self.url.format(ns=self.namespace.id),
                                   data={'name': 'myrepo1'})
        assert response.status_code == http_codes.HTTP_200_OK

        data = response.json()
        assert data['count'] == 1

        results = data['results']
        assert len(results) == 1

        self.assertDictContainsSubset({
            'name': 'myrepo1',
            'type': 'repository',
        }, results[0])

    def test_fail_method_not_allowed(self):
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            response = self.client.generic(method, self.url.format(ns=1))
            assert (response.status_code
                    == http_codes.HTTP_405_METHOD_NOT_ALLOWED)
