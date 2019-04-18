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
from rest_framework import views
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import semantic_version

from galaxy.main import models
from galaxy.api.v2 import serializers
from galaxy.api.v2.pagination import CustomPagination


__all__ = (
    'CollectionArtifactView',
    'VersionListView',
    'VersionDetailView',
)


# TODO(awcrosby): Move to views/utils.py and reuse across views
def _lookup_collection(kwargs):
    """Helper method to get collection from id, or namespace and name."""
    pk = kwargs.get('pk', None)
    ns_name = kwargs.get('namespace', None)
    name = kwargs.get('name', None)

    if pk:
        return get_object_or_404(models.Collection, pk=pk)

    ns = get_object_or_404(models.Namespace, name=ns_name)
    return get_object_or_404(models.Collection, namespace=ns, name=name)


class VersionListView(generics.ListAPIView):
    permission_classes = (AllowAny, )
    serializer_class = serializers.VersionSummarySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        """Return list of versions for a specific collection."""
        collection = _lookup_collection(self.kwargs)
        return models.CollectionVersion.objects.filter(collection=collection)

    def list(self, request, *args, **kwargs):
        """Override drf ListModelMixin to sort versions by semver."""
        queryset = self.filter_queryset(self.get_queryset())

        data = sorted(queryset,
                      key=lambda x: semantic_version.Version(x.version),
                      reverse=True)

        page = self.paginate_queryset(data)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class VersionDetailView(views.APIView):
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        """Return a collection version."""
        version = self._get_version()
        serializer = serializers.VersionDetailSerializer(version)
        return Response(serializer.data)

    def _get_version(self):
        """
        Get collection version from either version id, or from
        collection namespace, collection name, and version string.
        """
        version_pk = self.kwargs.get('version_pk', None)
        version_str = self.kwargs.get('version', None)
        if version_pk:
            return get_object_or_404(models.CollectionVersion, pk=version_pk)
        else:
            collection = _lookup_collection(self.kwargs)
            return get_object_or_404(
                models.CollectionVersion,
                collection=collection,
                version=version_str,
            )


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
