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

import operator

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework.exceptions import (
    APIException, ValidationError, ErrorDetail
)

from galaxy.api.base import exception_handler


class TestExceptionHandler:

    def test_http_not_found(self):
        error = Http404('Not found.')
        response = exception_handler(error, None)
        assert response.data == {
            'code': 'not_found',
            'message': 'Not found.',
        }

    def test_http_permission_denied(self):
        error = PermissionDenied('Permission denied.')
        response = exception_handler(error, None)
        assert response.data == {
            'code': 'permission_denied',
            'message': 'You do not have permission to perform this action.',
        }

    def test_api_exc_string(self):
        error = APIException('Error message.')
        response = exception_handler(error, None)
        assert response.data == {
            'code': 'error',
            'message': 'Error message.',
        }

    def test_api_exc_string_w_code(self):
        error = APIException('Error message.', code='testcode')
        response = exception_handler(error, None)
        assert response.data == {
            'code': 'testcode',
            'message': 'Error message.',
        }

    def test_api_exc_list(self):
        error = APIException([
            'Error message 1.',
            'Error message 2.',
        ])
        response = exception_handler(error, None)
        assert response.data == {
            'code': 'error',
            'message': 'A server error occurred.',
            'errors': [
                {'code': 'error', 'message': 'Error message 1.'},
                {'code': 'error', 'message': 'Error message 2.'},
            ]
        }

    def test_validation_error_field_single(self):
        error = APIException({
            'non_field_errors': ['Error message.']
        })
        response = exception_handler(error, None)
        assert response.data == {
            'code': 'error',
            'message': 'Error message.',
        }

    def test_validation_error_field_multi(self):
        error = APIException({
            'non_field_errors': ['Error message 1.', 'Error message 2.']
        })
        response = exception_handler(error, None)
        assert response.data == {
            'code': 'error',
            'message': 'A server error occurred.',
            'errors': [
                {'code': 'error', 'message': 'Error message 1.'},
                {'code': 'error', 'message': 'Error message 2.'},
            ]
        }

    def test_validation_error_fields(self):
        error = ValidationError({
            'foo': 'Foo error message.',
            'bar': [
                ErrorDetail('First bar message.', code='conflict'),
                'Second bar message.'
            ],
            'non_field_errors': ['Other message.'],

        })
        response = exception_handler(error, None)

        data = response.data
        errors = sorted(data['errors'], key=operator.itemgetter('message'))
        assert data['code'] == 'invalid'
        assert data['message'] == 'Invalid input.'
        assert errors == [
            {
                'code': 'conflict',
                'message': 'First bar message.',
                'field': 'bar',
            },
            {
                'code': 'invalid',
                'message': 'Foo error message.',
                'field': 'foo'
            },
            {
                'code': 'invalid',
                'message': 'Other message.'
            },
            {
                'code': 'invalid',
                'message': 'Second bar message.',
                'field': 'bar'
            },
        ]
