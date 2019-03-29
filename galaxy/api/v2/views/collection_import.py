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

from django.shortcuts import get_object_or_404
from pulpcore import constants as pulp_const
from pulpcore.app import models as pulp_models
from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from galaxy.api.v2 import serializers
from galaxy.main import models


class CollectionImportView(views.APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        task = get_object_or_404(models.Task, pk=self.kwargs['pk'])

        data = serializers.BaseTaskSerializer(task).data
        data['result'] = None
        if task.state == pulp_const.TASK_STATES.COMPLETED:
            version = self._get_version(task)
            # FIXME(cutwater): Replace with proper serializer
            version_data = {
                'id': version.pk,
                'href': reverse('api:v2:collection-version-detail',
                                args=[version.pk]),
            }
            data['result'] = {'version': version_data}
        return Response(data)

    def _get_version(self, task):
        resource = task.created_resources.first()
        assert issubclass(resource.content_type.model_class(),
                          pulp_models.RepositoryVersion)
        # NOTE(cutwater): We assume that only one collection can be added
        version = resource.content_object.added().first().cast()
        assert isinstance(version, models.CollectionVersion)

        return version
