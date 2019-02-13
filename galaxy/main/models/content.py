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
from django.forms import model_to_dict
from django.urls import reverse

from galaxy import constants
from galaxy.main import fields

from .base import (
    CommonModelNameNotUnique,
    BaseModel,
    CommonModel,
    PrimordialModel
)


class Content(CommonModelNameNotUnique):
    """A class representing a user role."""

    class Meta:
        unique_together = [
            ('namespace', 'repository', 'name', 'content_type')
        ]
        ordering = ['namespace', 'repository', 'name', 'content_type']
        indexes = [
            psql_indexes.GinIndex(fields=['search_vector'])
        ]
    # Foreign keys
    # -------------------------------------------------------------------------

    dependencies = models.ManyToManyField(
        'Content',
        related_name='+',
        blank=True,
        editable=False,
    )
    platforms = models.ManyToManyField(
        'Platform',
        related_name='roles',
        verbose_name="Supported Platforms",
        blank=True,
        editable=False,
    )
    platforms.help_text = ""

    cloud_platforms = models.ManyToManyField(
        'CloudPlatform',
        related_name='roles',
        verbose_name="Cloud Platforms",
        blank=True,
        editable=False,
    )

    tags = models.ManyToManyField(
        'Tag',
        related_name='roles',
        verbose_name='Tags',
        blank=True,
        editable=False,
    )
    tags.help_text = ""

    repository = models.ForeignKey(
        'Repository',
        related_name='content_objects',
        editable=False,
        on_delete=models.CASCADE,
    )

    content_type = models.ForeignKey(
        'ContentType',
        related_name='content_objects',
        editable=False,
        on_delete=models.PROTECT,
    )
    namespace = models.ForeignKey(
        'Namespace',
        related_name='content_objects',
        on_delete=models.CASCADE,
    )
    readme = models.ForeignKey(
        'Readme',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    # Regular fields
    # -------------------------------------------------------------------------

    # TODO(cutwater): Constants left for compatibility reasons. Should be
    # removed in future.
    ANSIBLE = constants.RoleType.ANSIBLE.value
    CONTAINER = constants.RoleType.CONTAINER.value
    CONTAINER_APP = constants.RoleType.CONTAINER_APP.value
    DEMO = constants.RoleType.DEMO.value

    role_type = models.CharField(
        max_length=3,
        choices=constants.RoleType.choices(),
        null=True,
        blank=False,
        default=None,
        editable=False,
    )
    original_name = models.CharField(
        max_length=256,
        null=False
    )
    metadata = psql_fields.JSONField(
        null=False,
        default=dict,
    )
    github_default_branch = models.CharField(
        max_length=256,
        default='master',
        verbose_name="Default Branch"
    )
    container_yml = models.TextField(
        blank=True,
        null=True,
        verbose_name='container.yml'
    )
    min_ansible_version = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Min Ansible Version",
    )
    min_ansible_container_version = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Min Ansible Container Version",
    )
    license = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="License (optional)",
    )
    company = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Company Name (optional)",
    )
    is_valid = models.BooleanField(
        default=False,
        editable=False,
    )
    featured = models.BooleanField(
        default=False,
        editable=False,
    )
    imported = models.DateTimeField(
        null=True,
        verbose_name="Last Import"
    )
    quality_score = models.FloatField(
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    content_score = models.FloatField(
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    metadata_score = models.FloatField(
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    compatibility_score = models.FloatField(
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )

    search_vector = psql_search.SearchVectorField()

    # Other functions and properties
    # -------------------------------------------------------------------------

    def __str__(self):
        return "{}.{}".format(self.namespace.name, self.name)

    @property
    def github_user(self):
        return self.repository.github_user

    @property
    def github_repo(self):
        return self.repository.github_repo

    @property
    def travis_status_url(self):
        return self.repository.travis_status_url

    @property
    def travis_build_url(self):
        return self.repository.travis_build_url

    @property
    def download_count(self):
        return self.repository.download_count

    def get_absolute_url(self):
        return reverse('api:content_detail', args=(self.pk,))

    def get_last_import(self):
        try:
            return model_to_dict(self.repository.import_tasks.latest(),
                                 fields=('id', 'state'))
        except Exception:
            return dict()

    def get_unique_platforms(self):
        return [platform.name for platform in
                self.platforms.filter(active=True)
                    .order_by('name').distinct('name')]

    def get_cloud_platforms(self):
        return [cp.name for cp in self.cloud_platforms.filter(active=True)]

    def get_unique_platform_versions(self):
        return [platform.release for platform in
                self.platforms.filter(active=True)
                    .order_by('release').distinct('release')]

    def get_unique_platform_search_terms(self):
        # Fetch the unique set of aliases
        terms = []
        for platform in (
                self.platforms.filter(active=True)
                .exclude(alias__isnull=True).exclude(alias__exact='').all()):
            terms += platform.alias.split(' ')
        return set(terms)

    def get_username(self):
        return self.namespace

    # TODO(cutwater): Active field is not used for tags anymore.
    # get_tags() function should be replaced with tags property usage and
    # removed as well as an `active` field from Tag model.
    def get_tags(self):
        return [tag.name for tag in self.tags.filter(active=True)]

    # FIXME(cutwater): Refactor me
    def clean(self):
        if self.company and len(self.company) > 50:
            # add_message(import_task, u"WARNING",
            # u"galaxy_info.company exceeds max length of 50 in meta data")
            self.company = self.company[:50]

        if not self.description:
            # add_message(import_task, u"ERROR",
            # u"missing description. Add a description to GitHub
            # repo or meta data.")
            pass
        elif len(self.description) > 255:
            # add_message(import_task, u"WARNING",
            # u"galaxy_info.description exceeds max length
            # of 255 in meta data")
            self.description = self.description[:255]

        if not self.license:
            # add_message(import_task, u"ERROR",
            # u"galaxy_info.license missing value in meta data")
            pass
        elif len(self.license) > 50:
            # add_message(import_task, u"WARNING",
            # u"galaxy_info.license exceeds max length of 50 in meta data")
            self.license = self.license[:50]

        if (not self.min_ansible_version
                and self.role_type in (constants.RoleType.CONTAINER,
                                       constants.RoleType.ANSIBLE)):
            self.min_ansible_version = u'2.4'

        if (not self.min_ansible_container_version
                and self.role_type == constants.RoleType.CONTAINER_APP):
            self.min_ansible_container_version = u'0.9.0'


class ContentType(BaseModel):
    """A model that represents content type (e.g. role, module, etc.)."""
    name = models.CharField(max_length=512, unique=True, db_index=True,
                            choices=constants.ContentType.choices())
    description = fields.TruncatingCharField(
        max_length=255, blank=True, default='')

    @classmethod
    def get(cls, content_type):
        if isinstance(content_type, constants.ContentType):
            content_type = content_type.value
        return cls.objects.get(name=content_type)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api:content_type_detail', args=(self.pk,))


class Tag(CommonModel):
    """A class representing the tags that have been assigned to roles."""

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api:tag_detail', args=(self.pk,))

    def get_num_roles(self):
        return self.roles.filter(active=True, is_valid=True).count()


class Platform(CommonModelNameNotUnique):
    """A class representing the valid platforms a role supports."""

    class Meta:
        ordering = ['name', 'release']

    release = models.CharField(
        max_length=50,
        verbose_name="Distribution Release Version",
    )
    alias = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Search terms"
    )

    def __str__(self):
        return "{}-{}".format(self.name, self.release)

    def get_absolute_url(self):
        return reverse('api:platform_detail', args=(self.pk,))


class CloudPlatform(CommonModel):
    """A model representing the valid cloud platforms for role."""

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api:cloud_platform_detail', args=(self.pk,))


class Video(PrimordialModel):
    class Meta:
        verbose_name = "videos"

    url = models.CharField(
        max_length=256,
        blank=False,
        null=False
    )
    url.help_text = ""

    role = models.ForeignKey(
        'Content',
        related_name='videos',
        on_delete=models.CASCADE,
        null=True
    )
    role.help_text = ""
