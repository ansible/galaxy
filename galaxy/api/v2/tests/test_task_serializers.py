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

from collections import OrderedDict
from unittest import mock
import uuid

import pytest
from django.utils import timezone
from pulpcore import constants as pulp_const
from pulpcore.app import models as pulp_models
from rest_framework import exceptions as drf_exc
from rest_framework.test import APIRequestFactory
import semantic_version

from galaxy.main import models
from galaxy.api.v2 import serializers


class TestCollectionUploadSerializer:

    def test_deserialize(self):
        fp = mock.Mock()
        fp.name = 'testnamespace-testcollection-1.2.3.tar.gz'
        fp.size = 42

        serializer = serializers.CollectionUploadSerializer(data={'file': fp})
        serializer.is_valid(raise_exception=True)

        filename = serializer.validated_data['filename']
        assert filename.namespace == 'testnamespace'
        assert filename.name == 'testcollection'
        assert filename.version == semantic_version.Version('1.2.3')

    def test_deserialize_fail_invalid_flename(self):
        fp = mock.Mock()
        fp.name = 'testnamespace-testcollection.tar.gz'
        fp.size = 42

        serializer = serializers.CollectionUploadSerializer(data={'file': fp})

        with pytest.raises(drf_exc.ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        assert excinfo.value.detail['non_field_errors'] == [
            'Invalid filename. Expected: {namespace}-{name}-{version}.tar.gz']


class TestCollectionImportSerializer:

    def test_serialize(self):
        job_id = uuid.uuid4()
        now = timezone.now()
        messages = [
            {
                'level': 'INFO',
                'message': 'Task started',
                'time': 1554381159.9411337
            }
        ]
        lint_records = [
            {
                'code': 'TEST0001',
                'type': 'test',
                'message': 'Test lint record',
                'severity': 4,
                'score_type': 'test'
            }
        ]

        pulp_task = pulp_models.Task(
            pk=24,
            job_id=job_id,
            state=pulp_const.TASK_STATES.RUNNING,
            started_at=now,
            finished_at=None,
        )
        namespace = models.Namespace(
            id=22,
            name='testnamespace',
        )
        instance = models.CollectionImport(
            id=42,
            pulp_task=pulp_task,
            namespace=namespace,
            name='testcollection',
            version='1.2.3',
            messages=messages,
            lint_records=lint_records
        )

        # NOTE: request hostname used for serializing urls
        request = APIRequestFactory().post('http://testserver/')
        serializer = serializers.CollectionImportSerializer(
            instance, context={'request': request})

        assert serializer.data == {
            'id': 42,
            'job_id': str(job_id),
            'state': 'running',
            'started_at': timezone.localtime(now).isoformat(),
            'finished_at': None,
            'error': None,
            'namespace': {
                'id': 22,
                'href': 'http://testserver/api/v1/namespaces/22/',
                'name': 'testnamespace',
            },
            'name': 'testcollection',
            'version': '1.2.3',
            'imported_version': None,
            'lint_records': [
                {
                    'code': 'TEST0001',
                    'type': 'test',
                    'message': 'Test lint record',
                    'severity': 4,
                    'score_type': 'test'
                }
            ],
            'messages': [
                OrderedDict([
                    ('level', 'INFO'),
                    ('message', 'Task started'),
                    ('time', '2019-04-04T08:32:39.941134-04:00')
                ]),
            ]
        }
