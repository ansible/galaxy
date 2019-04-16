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

from django.shortcuts import redirect, get_object_or_404

from rest_framework import exceptions as drf_exc
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status as http_codes
from rest_framework import views

from galaxy.main import models


__all__ = (
    'CollectionVersionView',
    'CollectionArtifactView',
)


class CollectionVersionView(views.APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, **kwargs):
        raise drf_exc.APIException(
            detail='Not implemented',
            code=http_codes.HTTP_501_NOT_IMPLEMENTED)


# TODO(cutwater): Use internal redirect for nginx
class CollectionArtifactView(views.APIView):
    permission_classes = (AllowAny, )

    def get(self, request, pk=None, namespace=None, name=None, version=None):
        if pk is not None:
            version = get_object_or_404(models.CollectionVersion, pk=pk)
        else:
            version = get_object_or_404(
                models.CollectionVersion,
                collection__namespace__name__iexact=namespace,
                collection__name__iexact=name,
                version__exact=version,
            )
        return redirect(version.get_download_url())
