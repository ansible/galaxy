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

from django.contrib.postgres import indexes as psql_indexes
from django.contrib.postgres import fields as psql_fields
from django.contrib.postgres import search as psql_search
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from pulpcore.app import models as pulp_models

from . import mixins
from .namespace import Namespace


class Collection(mixins.TimestampsMixin, models.Model):
    """
    A model representing an Ansible Content Collection.

    :var name: Collection name.
    :var namespace: Reference to a collection nanespace.
    :var deprecated: Indicates if a collection is deprecated.
    :var tags: List of a last collection version tags.
    :var dependencies: List a last collection version direct??? dependencies.
    """

    namespace = models.ForeignKey(Namespace, on_delete=models.PROTECT)
    name = models.CharField(max_length=64)

    deprecated = models.BooleanField(default=False)

    # Search vector
    search_vector = psql_search.SearchVectorField(default='')
    # Community and quality score
    download_count = models.IntegerField(default=0)
    community_score = models.FloatField(default=0.0)

    # References
    tags = models.ManyToManyField('Tag')

    class Meta:
        unique_together = (
            'namespace',
            'name',
        )
        indexes = [
            psql_indexes.GinIndex(fields=['search_vector'])
        ]


class CollectionVersion(mixins.TimestampsMixin, pulp_models.Content):
    """
    A model representing an Ansible Content Collection version.

    :var version: Collection version string in semantic version format.
    :var hidden: Indicates if a version should not be displayed and allowed
        for installation.
    :var metadata: Collection metadata in JSON format.
    :var contents: Collection contents in JSON format.
    :var collection: A reference to a related collection object.
    """

    TYPE = 'collection-version'

    # Fields
    version = models.CharField(max_length=64)
    hidden = models.BooleanField(default=False)

    metadata = psql_fields.JSONField(default=dict)
    contents = psql_fields.JSONField(default=dict)
    quality_score = models.FloatField(
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )

    # References
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='versions')
    _content = models.OneToOneField(
        pulp_models.Content, on_delete=models.CASCADE, parent_link=True,
        related_name='+', db_column='id',
    )

    class Meta:
        unique_together = (
            'collection',
            'version',
        )
