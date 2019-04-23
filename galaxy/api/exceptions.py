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
"""
Base API exception classes.
"""
from rest_framework.exceptions import (
    APIException,
    PermissionDenied,
)
from rest_framework import status as http_codes


__all__ = (
    'APIException',
    'ConflictError',
    'PermissionDenied',
    'ValidationError',
)


class ValidationError(APIException):
    status_code = http_codes.HTTP_400_BAD_REQUEST
    default_detail = 'Validation error.'
    default_code = 'invalid'


class ConflictError(APIException):
    status_code = http_codes.HTTP_409_CONFLICT
    default_detail = 'Conflict.'
    default_code = 'conflict'
