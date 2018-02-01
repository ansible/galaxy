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

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.forms.models import model_to_dict
from django.contrib.postgres.fields import ArrayField

from galaxy.main import constants
from galaxy.main.fields import LooseVersionField, TruncatingCharField
from galaxy.main.mixins import DirtyMixin

__all__ = [
    'PrimordialModel', 'Platform', 'CloudPlatform', 'Category', 'Tag',
    'Content', 'ImportTask', 'ImportTaskMessage', 'ContentVersion',
    'UserAlias', 'NotificationSecret', 'Notification', 'Repository',
    'Subscription', 'Stargazer', 'Namespace', 'Provider', 'ProviderNamespace',
    'ContentBlock', 'ContentType'
]


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

    description = TruncatingCharField(max_length=255, blank=True, default='')
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
    A class represnting the valid categories (formerly tags) that can be assigned to a role.
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
    A class representing a mapping between users and aliases to allow for user renaming without breaking deps.
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
        return unicode("%s (alias of %s)" % (self.alias_name, self.alias_of.username))


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
    description = TruncatingCharField(max_length=255, blank=True, default='')

    @classmethod
    def get(cls, content_type):
        if isinstance(content_type, constants.ContentType):
            content_type = content_type.value
        return cls.objects.get(name=content_type)

    def __str__(self):
        return self.name


class Content(CommonModelNameNotUnique):
    """A class representing a user role."""

    class Meta:
        unique_together = [
            ('namespace', 'content_type', 'name')
        ]
        ordering = ['namespace', 'content_type', 'name']

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
        on_delete=models.PROTECT
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
        default=ANSIBLE,
        blank=False,
        editable=False,
    )
    original_name = models.CharField(
        max_length=256,
        null=False
    )
    github_default_branch = models.CharField(
        max_length=256,
        default='master',
        verbose_name="Default Branch"
    )
    readme = models.TextField(
        blank=True,
        default='',
        verbose_name='README raw content'
    )
    readme_type = models.CharField(
        max_length=5,
        null=True,
        verbose_name='README type'
    )
    readme_html = models.TextField(
        blank=True,
        default='',
        verbose_name='README HTML'
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
    issue_tracker_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Issue Tracker URL",
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
    imported = models.DateTimeField(
        null=True,
        verbose_name="Last Import"
    )
    download_count = models.IntegerField(
        default=0
    )

    # Other functions and properties
    # -------------------------------------------------------------------------

    def __unicode__(self):
        return "%s.%s" % (self.namespace, self.name)

    @property
    def github_user(self):
        return self.repository.github_user

    @property
    def github_repo(self):
        return self.repository.github_repo

    def get_last_import(self):
        try:
            return model_to_dict(self.repository.import_tasks.latest(),
                                 fields=('id', 'state'))
        except:
            return dict()

    def get_unique_platforms(self):
        return [platform.name for platform in self.platforms.filter(active=True).order_by('name').distinct('name')]

    def get_cloud_platforms(self):
        return [cp.name for cp in self.cloud_platforms.filter(active=True)]

    def get_unique_platform_versions(self):
        return [platform.release for platform in self.platforms.filter(active=True).order_by('release').distinct('release')]

    def get_unique_platform_search_terms(self):
        # Fetch the unique set of aliases
        terms = []
        for platform in self.platforms.filter(active=True).exclude(alias__isnull=True).exclude(alias__exact='').all():
            terms += platform.alias.split(' ')
        return set(terms)

    def get_username(self):
        return self.namespace

    def get_tags(self):
        return [tag.name for tag in self.tags.filter(active=True)]

    def validate_char_lengths(self):
        for field in self._meta.get_fields():
            if not field.is_relation and field.get_internal_type() == 'CharField':
                if isinstance(getattr(self, field.name), basestring) and len(getattr(self, field.name)) > field.max_length:
                    raise Exception("Content %s value exceeeds max length of %s." % (field.name, field.max_length))


class Namespace(CommonModel):
    """
    Represents the aggregation of multiple namespaces across providers.
    """

    class Meta:
        ordering = ('name',)

    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='namespaces',
        null=False,
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

    def get_absolute_url(self):
        return reverse('api:namespace_detail', args=(self.pk,))


class Provider(CommonModel):
    """
    Valid SCM providers (e.g., GitHub, GitLab, etc.)
    """

    class Meta:
        ordering = ('name',)


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
        editable=False,
        verbose_name="Avatar URL"
    )
    location = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Location"
    )
    company = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Company Name"
    )
    email = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Email Address"
    )
    html_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Web Site URL"
    )
    followers = models.IntegerField(
        null=True,
        editable=False,
        verbose_name="Followers"
    )


class ContentVersion(CommonModelNameNotUnique):
    class Meta:
        ordering = ('-loose_version',)

    # Foreign keys
    # -------------------------------------------------------------------------

    content = models.ForeignKey(
        Content,
        related_name='versions',
    )

    # Regular fields
    # -------------------------------------------------------------------------

    release_date = models.DateTimeField(
        blank=True,
        null=True,
    )
    loose_version = LooseVersionField(
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
        super(ContentVersion, self).save(*args, **kwargs)


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
        return "%d-%s-%s" % (self.task.id, self.message_type, self.message_text)


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

    github_reference = models.CharField(
        max_length=256,
        verbose_name="Github Reference",
        null=True,
        blank=True,
        default=''
    )
    alternate_role_name = models.CharField(
        max_length=256,
        verbose_name="Alternate Role Name",
        null=True,
        blank=True,
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

    def validate_char_lengths(self):
        for field in self._meta.get_fields():
            if not field.is_relation and field.get_internal_type() == 'CharField':
                # print "%s %s" % (field.name, field.max_length)
                if isinstance(getattr(self, field.name), basestring) and len(getattr(self, field.name)) > field.max_length:
                    raise Exception("Import Task %s value exceeeds max length of %s." % (field.name, field.max_length))


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
    messages = ArrayField(
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

    # Fields
    name = models.CharField(max_length=256)
    original_name = models.CharField(max_length=256, null=False)

    import_branch = models.CharField(max_length=256, null=True)
    is_enabled = models.BooleanField(default=False)

    # Repository attributes
    commit = models.CharField(max_length=256, blank=True, default='')
    commit_message = models.CharField(max_length=256, blank=True, default='')
    commit_url = models.CharField(max_length=256, blank=True, default='')
    commit_created = models.DateTimeField(
        null=True, verbose_name="Laste Commit DateTime")
    stargazers_count = models.IntegerField(default=0)
    watchers_count = models.IntegerField(default=0)
    forks_count = models.IntegerField(default=0)
    open_issues_count = models.IntegerField(default=0)

    @property
    def clone_url(self):
        return "https://github.com/{user}/{repo}.git".format(
            user=self.github_user,
            repo=self.github_repo
        )

    @property
    def github_user(self):
        return self.provider_namespace.name

    @property
    def github_repo(self):
        return self.name


class Subscription(PrimordialModel):
    class Meta:
        unique_together = ('owner', 'github_user', 'github_repo')
        ordering = ('owner', 'github_user', 'github_repo')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='subscriptions',
    )
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
