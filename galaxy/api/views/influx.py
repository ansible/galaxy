# (c) 2012-2018, Ansible by Red Hat
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

import logging
import datetime

from galaxy.main import models
from galaxy.api import serializers

from . import base_views

from rest_framework.response import Response
from rest_framework import views

logger = logging.getLogger(__name__)

__all__ = [
    'InfluxSession',
    'InfluxMetrics'
]


def set_cookie(response, session):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    response.set_cookie(
        'influx_session',
        session,
        expires=expiration
    )

    return response


class InfluxSession(base_views.ListCreateAPIView):
    model = models.InfluxSessionIdentifier
    serializer_class = serializers.InfluxSessionSerializer

    def post(self, request, *args, **kwargs):
        influx_session = ''
        if not request.COOKIES.get('influx_session'):
            influx_session = self.model.objects.create()
        else:
            influx_session = models.InfluxSessionIdentifier.objects.get(
                session_id=request.COOKIES.get('influx_session')
            )

        serializer = self.get_serializer(instance=influx_session)
        headers = self.get_success_headers(serializer.data)

        response = set_cookie(
            Response(serializer.data, headers=headers),
            influx_session.session_id
        )

        return response

    def get(self, request, *args, **kwargs):
        return ''


class InfluxMetrics(views.APIView):
    def get(self, request):
        # TODO: Return real response
        return Response('HOWDY')

    def post(self, request):
        serializer = self.load_serializer(request)
        if serializer:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(serializer.data)

        # TODO: Return real response
        return Response('NO GO')

    # Can't name this get_serializer() for some reason
    def load_serializer(self, request):
        if request.data['measurement'] in serializers.InfluxTypes:
            serializer_type = serializers.InfluxTypes[
                request.data['measurement']
            ]
            return serializer_type(data=request.data)
        else:
            return None
