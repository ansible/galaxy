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

from django.db import models
from pulpcore.app import models as pulp_models


class Collection(pulp_models.Content):
    """
    A model representing an Ansible Content Collection.
    """

    TYPE = 'collection'

    namespace = models.CharField(max_length=64)
    name = models.CharField(max_length=64)

    _content = models.OneToOneField(
        pulp_models.Content, on_delete=models.CASCADE, parent_link=True,
        related_name='+', db_column='id',
    )

    class Meta:
        unique_together = (
            'namespace',
            'name',
        )


class CollectionVersion(pulp_models.Content):
    """
    A model representing an Ansible Content Collection version.
    """

    TYPE = 'collection-version'

    version = models.CharField(max_length=32)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='versions')

    _content = models.OneToOneField(
        pulp_models.Content, on_delete=models.CASCADE, parent_link=True,
        related_name='+', db_column='id',
    )

    class Meta:
        unique_together = (
            'version',
            'collection',
        )
