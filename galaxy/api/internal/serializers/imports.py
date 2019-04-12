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

from rest_framework import serializers
from rest_framework.reverse import reverse

from galaxy import constants as const
from galaxy.main import models


TYPE_COLLECTION = 'collection'
TYPE_REPOSITORY = 'repository'


class CollectionImportTaskItem(serializers.ModelSerializer):
    href = serializers.HyperlinkedIdentityField(
        'api:v2:collection-import-detail')
    type = serializers.SerializerMethodField()
    state = serializers.CharField()
    started_at = serializers.DateTimeField()
    finished_at = serializers.DateTimeField()

    namespace = serializers.SerializerMethodField()

    class Meta:
        model = models.CollectionImport
        fields = ('id', 'href', 'type', 'state', 'started_at', 'finished_at',
                  'namespace', 'name', 'version')

    def get_type(self, obj):
        return TYPE_COLLECTION

    def get_namespace(self, obj: models.CollectionImport):
        ns = obj.namespace
        request = self.context.get('request')
        return {
            'id': ns.id,
            'href': reverse('api:namespace_detail',
                            kwargs={'pk': ns.id}, request=request),
            'name': ns.name,
        }


class RepositoryImportTaskItem(serializers.ModelSerializer):
    href = serializers.HyperlinkedIdentityField(
        'api:import_task_detail')
    type = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    started_at = serializers.DateTimeField(source='started')
    finished_at = serializers.DateTimeField(source='finished')

    namespace = serializers.SerializerMethodField()
    name = serializers.CharField(source='repository.name')

    class Meta:
        model = models.ImportTask
        fields = ('id', 'href', 'type', 'state', 'started_at', 'finished_at',
                  'namespace', 'name')

    def get_type(self, obj):
        return TYPE_REPOSITORY

    def get_state(self, obj):
        return const.ImportTaskState(obj.state).as_task_state()

    def get_namespace(self, obj: models.ImportTask):
        ns = obj.repository.provider_namespace.namespace
        request = self.context.get('request')
        return {
            'id': ns.id,
            'href': reverse('api:namespace_detail',
                            kwargs={'pk': ns.id}, request=request),
            'name': ns.name,
        }


SERIALIZER_BY_TYPE = {
    TYPE_COLLECTION: CollectionImportTaskItem,
    TYPE_REPOSITORY: RepositoryImportTaskItem,
}
