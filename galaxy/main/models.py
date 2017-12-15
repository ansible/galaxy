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
from django.utils.timezone import now

from django.contrib.postgres.fields import ArrayField

from galaxy.main.fields import LooseVersionField, TruncatingCharField
from galaxy.main.mixins import DirtyMixin

__all__ = [
    'PrimordialModel', 'Platform', 'CloudPlatform', 'Category', 'Tag',
    'Content', 'ImportTask', 'ImportTaskMessage', 'ContentVersion',
    'UserAlias', 'NotificationSecret', 'Notification', 'Repository',
    'Subscription', 'Stargazer', 'Namespace', 'ContentBlock'
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

    def save(self, *args, **kwargs):
        # For compatibility with Django 1.4.x, attempt to handle any calls to
        # save that pass update_fields.
        try:
            super(BaseModel, self).save(*args, **kwargs)
        except TypeError:
            if 'update_fields' not in kwargs:
                raise
            kwargs.pop('update_fields')
            super(BaseModel, self).save(*args, **kwargs)

    def hasattr(self, attr):
        return hasattr(self, attr)


class PrimordialModel(BaseModel):
    """Base model for CommonModel and CommonModelNameNotUnique."""

    class Meta:
        abstract = True

    description = TruncatingCharField(max_length=255, blank=True, default='')
    active = models.BooleanField(default=True, db_index=True)

    def mark_inactive(self, save=True):
        """Use instead of delete to rename and mark inactive."""

        if self.active:
            if 'name' in self._meta.get_all_field_names():
                self.original_name = self.name
                self.name = "_deleted_%s_%s" % (now().isoformat(), self.name)
            self.active = False
            if save:
                self.save()

    def mark_active(self, save=True):
        """
        If previously marked inactive, this function reverses the
        renaming and sets the active flag to true.
        """

        if not self.active:
            if self.original_name != "":
                self.name = self.original_name
                self.original_name = ""
            self.active = True
            if save:
                self.save()


class CommonModel(PrimordialModel):
    """A base model where the name is unique."""

    class Meta:
        abstract = True

    name = models.CharField(max_length=512, unique=True, db_index=True)
    original_name = models.CharField(max_length=512)


class CommonModelNameNotUnique(PrimordialModel):
    """A base model where the name is not unique."""

    class Meta:
        abstract = True

    name = models.CharField(max_length=512, unique=False, db_index=True)
    original_name = models.CharField(max_length=512)


# Actual models
# -----------------------------------------------------------------------------

class Category(CommonModel):
    """A class represnting the valid categories (formerly tags) that can be
    assigned to a role.
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
    """A class representing a mapping between users and aliases
    to allow for user renaming without breaking deps.
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


class Content(CommonModelNameNotUnique):
    """A class representing a user role."""

    class Meta:
        unique_together = [
            ('namespace', 'name')
        ]
        ordering = ['namespace', 'name']

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
        related_name='role',
        editable=False,
        on_delete=models.PROTECT
    )

    # Regular fields
    # -------------------------------------------------------------------------

    ANSIBLE = 'ANS'
    CONTAINER = 'CON'
    CONTAINER_APP = 'APP'
    DEMO = 'DEM'
    ROLE_TYPE_CHOICES = (
        (ANSIBLE, 'Ansible'),
        (CONTAINER, 'Container Enabled'),
        (CONTAINER_APP, 'Container App'),
        (DEMO, 'Demo')
    )
    role_type = models.CharField(
        max_length=3,
        choices=ROLE_TYPE_CHOICES,
        default=ANSIBLE,
        blank=False,
        editable=False,
    )
    namespace = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Namespace",
    )
    github_branch = models.CharField(
        max_length=256,
        blank=True,
        default='',
        verbose_name="Github Branch"
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

    # GitHub repo attributes
    @property
    def stargazers_count(self):
        return self.repository.stargazers_count

    @property
    def watchers_count(self):
        return self.repository.watchers_count

    @property
    def forks_count(self):
        return self.repository.forks_count

    @property
    def open_issues_count(self):
        return self.repository.open_issues_count

    @property
    def commit(self):
        return self.repository.commit

    @property
    def commit_message(self):
        return self.repository.commit_message

    @property
    def commit_url(self):
        return self.repository.commit_url

    @property
    def commit_created(self):
        return self.repository.commit_created

    def get_last_import(self):
        try:
            return model_to_dict(self.import_tasks.latest(), fields=('id', 'state'))
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


class Namespace(PrimordialModel):

    class Meta:
        ordering = ('namespace',)

    namespace = models.CharField(
        max_length=256,
        unique=True,
        verbose_name="GitHub namespace"
    )
    name = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="GitHub name"
    )
    avatar_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="GitHub Avatar URL"
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
        verbose_name="Location"
    )
    email = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Location"
    )
    html_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="URL"
    )
    followers = models.IntegerField(
        null=True,
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


class ImportTask(PrimordialModel):
    class Meta:
        ordering = ('-id',)
        get_latest_by = 'created'

    github_user = models.CharField(
        max_length=256,
        verbose_name="Github Username",
    )
    github_repo = models.CharField(
        max_length=256,
        verbose_name="Github Repository",
    )
    github_reference = models.CharField(
        max_length=256,
        verbose_name="Github Reference",
        null=True,
        blank=True,
        default=''
    )
    role = models.ForeignKey(
        Content,
        related_name='import_tasks',
        db_index=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='import_tasks',
        db_index=True,
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
        default='PENDING',
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
    stargazers_count = models.IntegerField(
        default=0
    )
    watchers_count = models.IntegerField(
        default=0
    )
    forks_count = models.IntegerField(
        default=0
    )
    open_issues_count = models.IntegerField(
        default=0
    )
    github_branch = models.CharField(
        max_length=256,
        blank=True,
        default='',
        verbose_name="Github Branch"
    )
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
        return "%d-%s" % (self.id, self.started.strftime("%Y%m%d-%H%M%S-%Z"))

    def validate_char_lengths(self):
        for field in self._meta.get_fields():
            if not field.is_relation and field.get_internal_type() == 'CharField':
                # print "%s %s" % (field.name, field.max_length)
                if isinstance(getattr(self, field.name), basestring) and len(getattr(self, field.name)) > field.max_length:
                    raise Exception("Import Task %s value exceeeds max length of %s." % (field.name, field.max_length))


class ImportTaskMessage(PrimordialModel):
    task = models.ForeignKey(
        ImportTask,
        related_name='messages',
    )
    message_type = models.CharField(
        max_length=10,
    )
    message_text = models.CharField(
        max_length=256,
    )

    def __unicode__(self):
        return "%d-%s-%s" % (self.task.id, self.message_type, self.message_text)


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
        unique_together = ('github_user', 'github_repo')
        ordering = ('github_user', 'github_repo')

    # Foreign keys
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='repositories'
    )

    # Fields
    github_user = models.CharField(
        max_length=256,
        verbose_name="Github Username",
    )
    github_repo = models.CharField(
        max_length=256,
        verbose_name="Github Repository",
    )
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


class Subscription (PrimordialModel):
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


class Stargazer(PrimordialModel):
    class Meta:
        unique_together = ('owner', 'role')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='starred',
    )

    role = models.ForeignKey(
        Content,
        related_name='stars')


class RefreshRoleCount (PrimordialModel):
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
