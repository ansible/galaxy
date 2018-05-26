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

import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.forms.models import model_to_dict
from django.contrib.postgres import fields as psql_fields
from django.contrib.postgres import search as psql_search
from django.contrib.postgres import indexes as psql_indexes
from django.utils import timezone

from galaxy import constants
from galaxy.main import fields
from galaxy.main.mixins import DirtyMixin

logger = logging.getLogger(__name__)

__all__ = [
    'PrimordialModel', 'Platform', 'CloudPlatform', 'Category', 'Tag',
    'Content', 'ImportTask', 'ImportTaskMessage', 'RepositoryVersion',
    'UserAlias', 'NotificationSecret', 'Notification', 'Repository',
    'Subscription', 'Stargazer', 'Namespace', 'Provider', 'ProviderNamespace',
    'ContentBlock', 'ContentType'
]

# TODO(cutwater): Split models.py into multiple modules
# (e.g. models/base.py, models/content.py, etc.)


class BaseModel(models.Model, DirtyMixin):
    """Common model for objects not needing name, description,
    active attributes."""

    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        if hasattr(self, 'name'):
            return unicode("%s-%s" % (self.name, self.id))
        else:
            return u'%s-%s' % (self._meta.verbose_name, self.id)


class PrimordialModel(BaseModel):
    """Base model for CommonModel and CommonModelNameNotUnique."""

    class Meta:
        abstract = True

    description = fields.TruncatingCharField(
        max_length=255, blank=True, default='')
    active = models.BooleanField(default=True, db_index=True)


class CommonModel(PrimordialModel):
    """A base model where the name is unique."""

    class Meta:
        abstract = True

    name = models.CharField(max_length=512, unique=True, db_index=True)


class CommonModelNameNotUnique(PrimordialModel):
    """A base model where the name is not unique."""

    class Meta:
        abstract = True

    name = models.CharField(max_length=512, unique=False, db_index=True)


# Actual models
# -----------------------------------------------------------------------------

class Category(CommonModel):
    """
    A class represnting the valid categories (formerly tags)
    that can be assigned to a role.
    """

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api:category_detail', args=(self.pk,))


class Tag(CommonModel):
    """A class representing the tags that have been assigned to roles."""

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Tags'

    def __unicode__(self):
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

    def __unicode__(self):
        return "%s-%s" % (self.name, self.release)

    def get_absolute_url(self):
        return reverse('api:platform_detail', args=(self.pk,))


class CloudPlatform(CommonModel):
    """A model representing the valid cloud platforms for role."""

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api:cloud_platform_detail', args=(self.pk,))


class UserAlias(models.Model):
    """
    A class representing a mapping between users and aliases to allow
    for user renaming without breaking deps.
    """

    class Meta:
        verbose_name_plural = "UserAliases"

    alias_of = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='aliases',
    )
    alias_name = models.CharField(
        # must be in-sync with galaxy/accounts/models.py:CustomUser
        max_length=30,
        unique=True,
    )

    def __unicode__(self):
        return unicode("%s (alias of %s)" % (
            self.alias_name, self.alias_of.username))


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

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api:content_type_detail', args=(self.pk,))


class Content(CommonModelNameNotUnique):
    """A class representing a user role."""

    class Meta:
        unique_together = [
            ('namespace', 'content_type', 'name')
        ]
        ordering = ['namespace', 'content_type', 'name']
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

    categories = models.ManyToManyField(
        'Category',
        related_name='categories',
        verbose_name="Categories",
        blank=True,
        editable=False,
    )
    categories.help_text = ""

    repository = models.ForeignKey(
        'Repository',
        related_name='content_objects',
        editable=False,
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
    )
    readme = models.ForeignKey(
        'Readme',
        null=True,
        on_delete=models.PROTECT,
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
    metadata = fields.JSONField(
        null=False,
        default={}
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
    download_count = models.IntegerField(
        default=0
    )

    search_vector = psql_search.SearchVectorField()

    # Other functions and properties
    # -------------------------------------------------------------------------

    def __unicode__(self):
        return "%s.%s" % (self.namespace.name, self.name)

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
            # LOG.warn('Minimum Ansible version is not set, '
            #          'setting it to "1.9"')
            self.min_ansible_version = u'1.9'

        if (not self.min_ansible_container_version
                and self.role_type == constants.RoleType.CONTAINER_APP):
            # LOG.warn(u'Minimum Ansible Container version is not set, '
            #          u'setting it to "0.2.0"')
            self.min_ansible_container_version = u'0.2.0'


class Namespace(CommonModel):
    """
    Represents the aggregation of multiple namespaces across providers.
    """

    class Meta:
        ordering = ('name',)

    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='namespaces',
        editable=True,
    )
    avatar_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Avatar URL"
    )
    location = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Location"
    )
    company = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Company Name"
    )
    email = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Email Address"
    )
    html_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Web Site URL"
    )

    is_vendor = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('api:namespace_detail', args=(self.pk,))

    @property
    def content_counts(self):
        return Content.objects \
            .filter(namespace=self.pk) \
            .values('content_type__name') \
            .annotate(count=models.Count('content_type__name')) \
            .order_by('content_type__name')


class Provider(CommonModel):
    """
    Valid SCM providers (e.g., GitHub, GitLab, etc.)
    """

    class Meta:
        ordering = ('name',)

    def get_absolute_url(self):
        return reverse('api:active_provider_detail', args=(self.pk,))


class ProviderNamespace(PrimordialModel):
    """
    A one-to-one mapping to namespaces within each provider.
    """

    class Meta:
        ordering = ('provider', 'name')
        unique_together = [
            ('provider', 'name'),
            ('namespace', 'provider', 'name'),
        ]

    name = models.CharField(
        max_length=256,
        verbose_name="Name",
        editable=True,
        null=False
    )
    namespace = models.ForeignKey(
        'Namespace',
        related_name='provider_namespaces',
        editable=False,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Namespace'
    )
    provider = models.ForeignKey(
        'Provider',
        related_name='provider_namespaces',
        editable=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Provider'
    )
    display_name = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Display Name"
    )
    avatar_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=True,
        verbose_name="Avatar URL"
    )
    location = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=True,
        verbose_name="Location"
    )
    company = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=True,
        verbose_name="Company Name"
    )
    email = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=True,
        verbose_name="Email Address"
    )
    html_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=True,
        verbose_name="Web Site URL"
    )
    followers = models.IntegerField(
        null=True,
        editable=True,
        verbose_name="Followers"
    )

    def get_absolute_url(self):
        return reverse('api:provider_namespace_detail', args=(self.pk,))


class RepositoryVersion(CommonModelNameNotUnique):
    class Meta:
        ordering = ('-loose_version',)
        unique_together = ('repository', 'name')

    # Foreign keys
    # -------------------------------------------------------------------------

    repository = models.ForeignKey(
        'Repository',
        related_name='versions'
    )

    # Regular fields
    # -------------------------------------------------------------------------

    release_date = models.DateTimeField(
        blank=True,
        null=True,
    )
    loose_version = fields.LooseVersionField(
        editable=False,
        db_index=True,
    )

    # Other functions and properties
    # -------------------------------------------------------------------------

    def __unicode__(self):
        return "%s.%s-%s" % (self.content.namespace,
                             self.content.name, self.name)

    def save(self, *args, **kwargs):
        # the value of score is based on the
        # values in the other rating fields
        self.loose_version = self.name
        super(RepositoryVersion, self).save(*args, **kwargs)


class ImportTaskMessage(PrimordialModel):
    TYPE_INFO = constants.ImportTaskMessageType.INFO.value
    TYPE_WARNING = constants.ImportTaskMessageType.WARNING.value
    TYPE_SUCCESS = constants.ImportTaskMessageType.SUCCESS.value
    # FIXME(cutwater): ERROR and FAILED types seem to be redundant
    TYPE_FAILED = constants.ImportTaskMessageType.FAILED.value
    TYPE_ERROR = constants.ImportTaskMessageType.ERROR.value

    task = models.ForeignKey(
        'ImportTask',
        related_name='messages',
    )
    message_type = models.CharField(
        max_length=10,
        choices=constants.ImportTaskMessageType.choices(),
    )
    message_text = models.CharField(
        max_length=256,
    )

    def __unicode__(self):
        return "%d-%s-%s" % (
            self.task.id, self.message_type, self.message_text)


class ImportTask(PrimordialModel):
    class Meta:
        ordering = ('-id',)
        get_latest_by = 'created'

    # TODO(cutwater): Constants left for backward compatibility, to be removed
    STATE_PENDING = constants.ImportTaskState.PENDING.value
    STATE_RUNNING = constants.ImportTaskState.RUNNING.value
    STATE_FAILED = constants.ImportTaskState.FAILED.value
    STATE_SUCCESS = constants.ImportTaskState.SUCCESS.value

    repository = models.ForeignKey(
        'Repository',
        related_name='import_tasks',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='import_tasks',
        db_index=True,
    )
    import_branch = models.CharField(
        max_length=256,
        null=True,
        blank=False,
    )
    repository_alt_name = models.CharField(
        max_length=256,
        null=True,
        blank=False,
    )
    celery_task_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    state = models.CharField(
        max_length=20,
        default=STATE_PENDING,
        choices=constants.ImportTaskState.choices()
    )
    started = models.DateTimeField(
        auto_now_add=False,
        null=True,
        blank=True,
    )
    finished = models.DateTimeField(
        auto_now_add=False,
        null=True,
        blank=True,
    )

    # GitHub repo attributes at time of import
    commit = models.CharField(
        max_length=256,
        blank=True
    )
    commit_message = models.CharField(
        max_length=256,
        blank=True
    )
    commit_url = models.CharField(
        max_length=256,
        blank=True
    )
    travis_status_url = models.CharField(
        max_length=256,
        blank=True,
        default='',
        verbose_name="Travis Build Status"
    )
    travis_build_url = models.CharField(
        max_length=256,
        blank=True,
        default='',
        verbose_name="Travis Build URL"
    )

    def __unicode__(self):
        return u'{}-{}'.format(self.id, self.state)

    def start(self):
        self.state = ImportTask.STATE_RUNNING
        self.started = timezone.now()
        self.save()

    def finish_success(self, message=None):
        self.state = ImportTask.STATE_SUCCESS
        self.finished = timezone.now()
        if message:
            self.messages.create(message_type=ImportTaskMessage.TYPE_SUCCESS,
                                 message_text=message)
        self.save()

    def finish_failed(self, reason=None):
        self.state = ImportTask.STATE_FAILED
        self.finished = timezone.now()
        if reason:
            # FIXME(cutwater): Remove truncating reason to 256 chars.
            # Use TruncatingCharField or TextField for message field
            self.messages.create(message_type=ImportTaskMessage.TYPE_FAILED,
                                 message_text=str(reason)[:256])
        self.save()


class NotificationSecret(PrimordialModel):
    class Meta:
        ordering = ('source', 'github_user', 'github_repo')
        unique_together = ('source', 'github_user', 'github_repo')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notification_secrets',
        db_index=True,
    )
    source = models.CharField(
        max_length=20,
        verbose_name="Source"
    )
    github_user = models.CharField(
        max_length=256,
        verbose_name="Github Username",
    )
    github_repo = models.CharField(
        max_length=256,
        verbose_name="Github Repository",
    )
    secret = models.CharField(
        max_length=256,
        verbose_name="Secret",
        db_index=True
    )

    def __unicode__(self):
        return "%s-%s" % (self.owner.username, self.source)

    def repo_full_name(self):
        return "%s/%s" % (self.github_user, self.github_repo)


class Notification(PrimordialModel):
    class Meta:
        ordering = ('-id',)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        db_index=True,
        editable=False
    )
    source = models.CharField(
        max_length=20,
        verbose_name="Source",
        editable=False
    )
    github_branch = models.CharField(
        max_length=256,
        verbose_name="GitHub Branch",
        blank=True,
        editable=False
    )
    travis_build_url = models.CharField(
        max_length=256,
        blank=True
    )
    travis_status = models.CharField(
        max_length=256,
        blank=True
    )
    commit = models.CharField(
        max_length=256,
        blank=True
    )
    committed_at = models.DateTimeField(
        auto_now=False,
        null=True
    )
    commit_message = models.CharField(
        max_length=256,
        blank=True
    )
    roles = models.ManyToManyField(
        Content,
        related_name='notifications',
        verbose_name='Roles',
        editable=False
    )
    imports = models.ManyToManyField(
        ImportTask,
        related_name='notifications',
        verbose_name='Tasks',
        editable=False
    )
    messages = psql_fields.ArrayField(
        models.CharField(max_length=256),
        default=list,
        editable=False
    )


class Repository(BaseModel):
    class Meta:
        unique_together = ('provider_namespace', 'name')
        ordering = ('provider_namespace', 'name')

    # Foreign keys
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='repositories'
    )
    provider_namespace = models.ForeignKey(
        ProviderNamespace,
        related_name='repositories',
    )
    readme = models.ForeignKey(
        'Readme',
        null=True,
        on_delete=models.PROTECT,
        related_name='+',
    )

    # Fields
    name = models.CharField(max_length=256)
    original_name = models.CharField(max_length=256, null=False)
    format = models.CharField(max_length=16, null=True,
                              choices=constants.RepositoryFormat.choices())
    description = fields.TruncatingCharField(
        max_length=255, blank=True, default='')
    import_branch = models.CharField(max_length=256, null=True)
    is_enabled = models.BooleanField(default=False)

    # Repository attributes
    commit = models.CharField(max_length=256, blank=True, default='')
    commit_message = fields.TruncatingCharField(
        max_length=256, blank=True, default='')
    commit_url = models.CharField(max_length=256, blank=True, default='')
    commit_created = models.DateTimeField(
        null=True, verbose_name="Last Commit DateTime")
    stargazers_count = models.IntegerField(default=0)
    watchers_count = models.IntegerField(default=0)
    forks_count = models.IntegerField(default=0)
    open_issues_count = models.IntegerField(default=0)
    travis_status_url = models.CharField(
        max_length=256,
        blank=True,
        default='',
        verbose_name="Travis Build Status"
    )
    travis_build_url = models.CharField(
        max_length=256,
        blank=True,
        default='',
        verbose_name="Travis Build URL"
    )
    issue_tracker_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Issue Tracker URL",
    )

    @property
    def clone_url(self):
        return "https://github.com/{user}/{repo}.git".format(
            user=self.provider_namespace.name,
            repo=self.original_name
        )

    @property
    def github_user(self):
        return self.provider_namespace.name

    @property
    def github_repo(self):
        return self.original_name

    @property
    def content_counts(self):
        return Content.objects \
            .filter(repository=self.pk) \
            .values('content_type__name') \
            .annotate(count=models.Count('content_type__name')) \
            .order_by('content_type__name')

    def get_absolute_url(self):
        return reverse('api:repository_detail', args=(self.pk,))


class Subscription(PrimordialModel):
    class Meta:
        unique_together = ('owner', 'github_user', 'github_repo')
        ordering = ('owner', 'github_user', 'github_repo')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='subscriptions',
    )
    # TODO(cutwater): Replace with reference to a Repository model
    github_user = models.CharField(
        max_length=256,
        verbose_name="Github Username",
    )
    github_repo = models.CharField(
        max_length=256,
        verbose_name="Github Repository",
    )


class Stargazer(BaseModel):
    class Meta:
        unique_together = ('owner', 'repository')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='starred',
    )

    repository = models.ForeignKey(
        Repository,
        related_name='stars'
    )


class RefreshRoleCount(PrimordialModel):
    state = models.CharField(
        max_length=20
    )
    passed = models.IntegerField(
        default=0,
        null=True
    )
    failed = models.IntegerField(
        default=0,
        null=True
    )
    deleted = models.IntegerField(
        default=0,
        null=True
    )
    updated = models.IntegerField(
        default=0,
        null=True
    )


class ContentBlock(BaseModel):
    name = models.SlugField(unique=True)
    content = models.TextField('content', blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api:content_block_detail', args=(self.name,))


class Readme(BaseModel):
    class Meta:
        unique_together = ('repository', 'raw_hash')

    repository = models.ForeignKey(
        Repository,
        null=False,
        on_delete=models.CASCADE,
        related_name='+',
    )
    raw = models.TextField(null=False, blank=False)
    raw_hash = models.CharField(
        max_length=128, null=False, blank=False)
    mimetype = models.CharField(max_length=32, blank=False)
    html = models.TextField(null=False, blank=False)

    def safe_delete(self):
        ref_count = (
            Repository.objects.filter(readme=self).count()
            + Content.objects.filter(readme=self).count()
        )
        if ref_count:
            return False

        self.delete()
        return True
