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

import collections

from django.db.models import fields
from django.db.models import F, Value

from rest_framework import generics


from galaxy.main import models
from galaxy.api.internal.serializers.imports import (
    TYPE_REPOSITORY, TYPE_COLLECTION, SERIALIZER_BY_TYPE
)

__all__ = (
    'NamespaceImportsList',
)


class NamespaceImportsList(generics.ListAPIView):

    QS_BY_TYPE = {
        TYPE_COLLECTION: (
            models.CollectionImport.objects
            .select_related('pulp_task', 'namespace')
            .all()
        ),
        TYPE_REPOSITORY: (
            models.ImportTask.objects
            .select_related('repository__provider_namespace__namespace')
            .all()
        ),
    }

    def list(self, request, *args, **kwargs):
        items = self.paginate_queryset(self.get_queryset())
        self.load_objects(items)
        result = self.serialize_objects(items)
        return self.get_paginated_response(result)

    def get_queryset(self):
        task_type = self.request.query_params.get('type')

        if task_type == TYPE_COLLECTION:
            qs = self.get_collection_queryset()
        elif task_type == TYPE_REPOSITORY:
            qs = self.get_repsository_queryset()
        else:
            qs = self.get_collection_queryset()
            qs = qs.union(self.get_repsository_queryset(), all=True)
        return qs.order_by('-started_at')

    def get_collection_queryset(self):
        namespace_id = self.kwargs['namespace_id']
        qs = (
            models.CollectionImport.objects
            .filter(namespace_id=namespace_id)
            .annotate(type=Value(TYPE_COLLECTION,
                                 output_field=fields.CharField()),
                      started_at=F('pulp_task__started_at'))
            .values('pk', 'type', 'started_at')
        )

        name = self.request.query_params.get('name')
        if name:
            qs = qs.filter(name__icontains=name)

        return qs

    def get_repsository_queryset(self):
        namespace_id = self.kwargs['namespace_id']
        qs = (
            models.ImportTask.objects
            .filter(
                repository__provider_namespace__namespace_id=namespace_id)
            .annotate(type=Value(TYPE_REPOSITORY,
                                 output_field=fields.CharField()),
                      started_at=F('started'))
            .values('pk', 'type', 'started_at')
            .order_by()
        )

        name = self.request.query_params.get('name')
        if name:
            qs = qs.filter(repository__name__icontains=name)

        return qs

    def load_objects(self, records):
        to_load = collections.defaultdict(list)
        for record in records:
            to_load[record['type']].append(record['pk'])

        loaded = {}
        for tp, ids in to_load.items():
            loaded[tp] = {
                obj.pk: obj for obj in self.QS_BY_TYPE[tp].filter(pk__in=ids)}

        for record in records:
            pk = record['pk']
            tp = record['type']
            record['object'] = loaded[tp][pk]

    def serialize_objects(self, records):
        for record in records:
            tp = record['type']
            obj = record['object']
            serializer_class = SERIALIZER_BY_TYPE[tp]
            serializer = serializer_class(
                obj, context={'request': self.request})
            yield serializer.data
