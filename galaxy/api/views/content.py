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

from galaxy.main import models
from galaxy.api import serializers

from . import base_views as base


__all__ = (
    'ContentList',
    'ContentDetail',
)


class ContentList(base.ListAPIView):

    model = models.Content
    serializer_class = serializers.ContentSerializer

    QUERY_FIELDS = (
        'id',
        'name',
        'description',
        'created',
        'modified',
        'imported',
        'namespace__name',
        'content_type__name',
        'repository__name'
    )

    def get_queryset(self):
        return (
            super(ContentList, self).get_queryset()
            .filter(
                repository__provider_namespace__namespace__isnull=False,
                repository__provider_namespace__namespace__active=True
            )
            .only(*self.QUERY_FIELDS)
            .select_related(
                'namespace',
                'content_type',
                'repository'
            )
            .prefetch_related(
                'platforms',
                'cloud_platforms',
                'tags',
                'versions',
            )
        )


class ContentDetail(base.RetrieveAPIView):

    model = models.Content
    serializer_class = serializers.ContentDetailSerializer

    QUERY_FIELDS = ContentList.QUERY_FIELDS + (
        'readme',
        'readme_html',
        'metadata',
    )
