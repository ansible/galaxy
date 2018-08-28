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

from rest_framework import serializers as drf_serializers
from galaxy.main import models
from galaxy.api import serializers

from . import base_views

from rest_framework.response import Response

logger = logging.getLogger(__name__)

__all__ = [
    'EventList',
    'EventDetail'
]


class EventList(base_views.ListCreateAPIView):
    model = models.SessionEvent
    serializer_class = serializers.EventSerializer

    def post(self, request, *args, **kwargs):
        if not request.session.get('session_id'):
            request.session['session_id'] = str(
                models.SessionIdentifier.objects.create())
        request.data['session_id'] = request.session['session_id']
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)


class EventDetail(base_views.RetrieveUpdateAPIView):
    model = models.SessionEvent
    serializer_class = serializers.EventSerializer

    def update(self, request, *args, **kwargs):
        if not request.session.get('session_id'):
            request.session['session_id'] = str(
                models.SessionIdentifier.objects.create())
        request.data['session_id'] = request.session['session_id']
        instance = self.get_object()
        if str(instance.session_id.session_id) != request.data['session_id']:
            message = ('Request session_id %s does not match '
                       'existing event object.' % request.data['session_id'])
            raise drf_serializers.ValidationError(message)
        return super(EventDetail, self).update(request, *args, **kwargs)
