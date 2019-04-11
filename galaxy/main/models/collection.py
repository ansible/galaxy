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

import logging

import attr
from django.contrib.postgres import indexes as psql_indexes
from django.contrib.postgres import fields as psql_fields
from django.contrib.postgres import search as psql_search
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from pulpcore.app import models as pulp_models
import semantic_version

from galaxy.importer.utils import lint as lintutils
from . import mixins
from .namespace import Namespace
from .task import Task
from .base import SurveyBase


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
    community_score = models.FloatField(null=True)
    community_survey_count = models.IntegerField(default=0)

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

    @property
    def latest_version(self):
        versions = self.versions.filter(hidden=False)
        if not versions:
            return None
        return versions.latest('pk')

    @property
    def highest_version(self):
        versions = self.versions.filter(hidden=False)
        if not versions:
            return None

        d = {semantic_version.Version(v.version): v for v in versions}
        highest = semantic_version.Spec('*').select(d.keys())
        return d[highest]


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

    readme_mimetype = models.CharField(max_length=32, blank=True)
    readme_text = models.TextField(blank=True)
    readme_html = models.TextField(blank=True)

    # References
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='versions')
    _parent_ref = models.OneToOneField(
        pulp_models.Content, on_delete=models.CASCADE,
        parent_link=True, db_column='id'
    )

    class Meta:
        unique_together = (
            'collection',
            'version',
        )


class CollectionImport(Task):
    """Collection import task info."""

    name = models.CharField(max_length=64)
    version = models.CharField(max_length=64)

    messages = psql_fields.JSONField(default=list)
    lint_records = psql_fields.JSONField(default=list)

    namespace = models.ForeignKey(Namespace, on_delete=models.CASCADE)
    imported_version = models.ForeignKey(
        CollectionVersion, null=True, on_delete=models.SET_NULL,
        related_name='import_tasks')

    def add_log_record(self, record: logging.LogRecord):
        self.messages.append({
            'message': record.msg,
            'level': record.levelname,
            'time': record.created,
        })

    def add_lint_record(self, lint_record: lintutils.LintRecord) -> None:
        self.lint_records.append(attr.asdict(lint_record))

    def get_message_stats(self):
        """Returns total number of errors and warnings."""
        # TODO(cutwater): Replace with SQL query
        errors, warnings = 0, 0
        for msg in self.messages:
            if msg['level'] == 'ERROR':
                errors += 1
            elif msg['level'] == 'WARNING':
                warnings += 1
        return errors, warnings


class CollectionSurvey(SurveyBase):
    class Meta:
        unique_together = ('user', 'collection')

    collection = models.ForeignKey(
        Collection,
        null=False,
        on_delete=models.CASCADE,
    )
