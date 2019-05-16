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
from rest_framework import response
from rest_framework import exceptions as drf_exceptions
from django.core import exceptions

from galaxy.api import base
from galaxy.main import models


class ContentTypeView(base.APIView):
    def get(self, request):
        namespace = request.GET.get('namespace', None)
        name = request.GET.get('name', None)

        if not name or not namespace:
            raise drf_exceptions.ValidationError(
                detail='namespace and name parameters are required')

        try:
            models.Repository.objects.get(
                provider_namespace__namespace__name=namespace,
                name=name
            )
            return response.Response({'type': 'repository'})
        except exceptions.ObjectDoesNotExist:
            pass

        try:
            models.Collection.objects.get(
                namespace__name=namespace,
                name=name
            )
            return response.Response({'type': 'collection'})
        except exceptions.ObjectDoesNotExist:
            raise drf_exceptions.NotFound(
                detail="No collection or repository could be found " +
                "matching the name {}.{}".format(namespace, name)
            )
