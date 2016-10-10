# (c) 2012-2016, Ansible by Red Hat
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

# standard python libs

# django libs
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.forms.models import model_to_dict
from django.utils.timezone import now

# postgresql specific
from django.contrib.postgres.fields import ArrayField

# local stuff
from galaxy.main.fields import LooseVersionField, TruncatingCharField
from galaxy.main.mixins import DirtyMixin

__all__ = [
    'PrimordialModel', 'Platform', 'Category', 'Tag', 'Role', 'ImportTask', 'ImportTaskMessage', 'RoleRating', 
    'RoleVersion', 'UserAlias', 'NotificationSecret', 'Notification', 'Repository', 'Subscription', 'Stargazer',
    'Namespace'
]

###################################################################################
# Our custom user class, brought in here so it can be used commonly throughout
# the rest of the codebase

#User = get_user_model()

###################################################################################
# Abstract models that form a base for all real models


class BaseModel(models.Model, DirtyMixin):
    '''
    common model for objects not needing name, description, active attributes
    '''

    class Meta:
        abstract = True

    created       = models.DateTimeField(auto_now_add=True)
    modified      = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        if hasattr(self, 'name'):
            return unicode("%s-%s"% (self.name, self.id))
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
    '''
    base model for CommonModel and CommonModelNameNotUnique
    '''

    class Meta:
        abstract = True

    description = TruncatingCharField(max_length=255, blank=True, default='')
    active      = models.BooleanField(default=True, db_index=True)

    def mark_inactive(self, save=True):
        '''Use instead of delete to rename and mark inactive.'''

        if self.active:
            if 'name' in self._meta.get_all_field_names():
                self.original_name = self.name
                self.name = "_deleted_%s_%s" % (now().isoformat(), self.name)
            self.active = False
            if save:
                self.save()

    def mark_active(self, save=True):
        '''
        If previously marked inactive, this function reverses the
        renaming and sets the active flag to true
        '''

        if not self.active:
            if self.original_name != "":
                self.name = self.original_name
                self.original_name = ""
            self.active = True
            if save:
                self.save()


class CommonModel(PrimordialModel):
    # a base model where the name is unique '''

    class Meta:
        abstract = True

    name = models.CharField(max_length=512, unique=True, db_index=True)
    original_name = models.CharField(max_length=512)

class CommonModelNameNotUnique(PrimordialModel):
    # a base model where the name is not unique '''

    class Meta:
        abstract = True

    name = models.CharField(max_length=512, unique=False, db_index=True)
    original_name = models.CharField(max_length=512)

###################################################################################
# Actual models

class Category(CommonModel):
    #
    # a class represnting the valid categories (formerly tags) that can be
    # assigned to a role

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api:category_detail', args=(self.pk,))

    #def get_num_roles(self):
    #    return self.roles.filter(active=True, owner__is_active=True).count()

class Tag(CommonModel):
    #
    # a class representing the tags that have been assigned to roles

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
    # a class represnting the valid platforms a role supports '''

    class Meta:
        ordering = ['name','release']

    release = models.CharField(
        max_length   = 50,
        verbose_name = "Distribution Release Version",
    )
    alias = models.CharField(
        max_length   = 256,
        blank        = True,
        null         = True,
        verbose_name = "Search terms"
    )

    def __unicode__(self):
        return "%s-%s" % (self.name, self.release)

    def get_absolute_url(self):
        return reverse('api:platform_detail', args=(self.pk,))

class UserAlias(models.Model):
    #
    # a class representing a mapping between users and aliases
    # to allow for user renaming without breaking deps

    class Meta:
        verbose_name_plural = "UserAliases"

    alias_of = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = 'aliases',
    )
    alias_name = models.CharField(
        # must be in-sync with galaxy/accounts/models.py:CustomUser
        max_length   = 30,
        unique       = True,
    )

    def __unicode__(self):
        return unicode("%s (alias of %s)"% (self.alias_name, self.alias_of.username))

class Role(CommonModelNameNotUnique):
    # a class representing a user role

    class Meta:
        unique_together = ('namespace','name')
        ordering = ['namespace', 'name']

    #
    #  ------------------------------------------------------------------------------
    # foreign keys

    dependencies = models.ManyToManyField(
        'Role',
        related_name = '+',
        blank        = True,
        editable     = False,
    )
    platforms = models.ManyToManyField(
        'Platform',
        related_name = 'roles',
        verbose_name = "Supported Platforms",
        blank        = True,
        editable     = False,
    )
    platforms.help_text = ""

    tags = models.ManyToManyField(
        'Tag',
        related_name = 'roles',
        verbose_name = 'Tags',
        blank        = True,
        editable     = False,    
    )
    tags.help_text = ""

    categories = models.ManyToManyField(
        'Category',
        related_name = 'categories',
        verbose_name = "Categories",
        blank        = True,
        editable     = False,    
    )
    categories.help_text = ""

    #
    # ------------------------------------------------------------------------------
    # regular fields
    ANSIBLE = 'ANS'
    CONTAINER = 'CON'
    CONTAINER_APP = 'APP'
    ROLE_TYPE_CHOICES = (
        (ANSIBLE, 'Ansible'),
        (CONTAINER, 'Container Enabled'),
        (CONTAINER_APP, 'Container App')
    )
    role_type = models.CharField(
        max_length=3,
        choices=ROLE_TYPE_CHOICES,
        default=ANSIBLE,
        blank=False,
        editable=False,
    )
    namespace = models.CharField(
        max_length   = 256,
        blank        = True,
        null         = True,
        verbose_name = "Namespace",
    )
    github_user = models.CharField(
        max_length   = 256,
        verbose_name = "Github Username",
    )
    github_repo = models.CharField(
        max_length   = 256,
        verbose_name = "Github Repository",
    )
    github_branch = models.CharField(
        max_length   = 256,
        blank        = True,
        default      = '',
        verbose_name = "Github Branch"
    )
    github_default_branch = models.CharField(
        max_length   = 256,
        default      = 'master',
        verbose_name = "Default Branch"
    )
    readme = models.TextField(
        blank        = True,
        default      = '',
        verbose_name = 'README raw content'
    )
    readme_type = models.CharField(
        max_length   = 5,
        null         = True,
        verbose_name = 'README type'
    )
    readme_html = models.TextField(
        blank        = True,
        default      = '',
        verbose_name = 'README HTML'
    )
    container_yml = models.TextField(
        blank        = True,
        null         = True,
        verbose_name = 'container.yml'
    )
    min_ansible_version = models.CharField(
        max_length   = 10,
        blank        = True,
        null         = True,
        verbose_name = "Min Ansible Version",
    )
    min_ansible_container_version = models.CharField(
        max_length   = 10,
        blank        = True,
        null         = True,
        verbose_name = "Min Ansible Container Version",
    )
    issue_tracker_url = models.CharField(
        max_length   = 256,
        blank        = True,
        null         = True,
        verbose_name = "Issue Tracker URL",
    )
    license = models.CharField(
        max_length   = 50,
        blank        = True,
        verbose_name = "License (optional)",
    )
    company = models.CharField(
        max_length   = 50,
        blank        = True,
        null         = True,
        verbose_name = "Company Name (optional)",
    )
    is_valid = models.BooleanField(
        default      = False,
        editable     = False,
    )
    featured = models.BooleanField(
        default      = False,
        editable     = False,
    )
    travis_status_url = models.CharField(
        max_length   = 256,
        blank        = True,
        default      = '',
        verbose_name = "Travis Build Status"
    )
    travis_build_url = models.CharField(
        max_length   = 256,
        blank        = True,
        default      = '',
        verbose_name = "Travis Build URL"
    )
    imported         = models.DateTimeField(
        null         = True,
        verbose_name = "Last Import"
    )
    download_count   = models.IntegerField(
        default      = 0
    )

    # GitHub repo attributes
    stargazers_count = models.IntegerField(
        default      = 0
    )
    watchers_count   = models.IntegerField(
        default      = 0
    )
    forks_count      = models.IntegerField(
        default      = 0
    )
    open_issues_count = models.IntegerField(
        default      = 0
    )
    commit           = models.CharField(
        max_length   = 256,
        blank        = True
    )
    commit_message   = models.CharField(
        max_length   = 256,
        blank        = True
    )
    commit_url       = models.CharField(
        max_length   = 256,
        blank        = True
    )
    commit_created = models.DateTimeField(
        null         = True,
        verbose_name = "Laste Commit DateTime"
    )
    
    #
    # #tags = ArrayField(models.CharField(max_length=256), null=True, editable=True, size=100)

    # ------------------------------------------------------------------------------
    # fields calculated by a celery task or signal, not set

    bayesian_score = models.FloatField(
        default    = 0.0,
        editable   = False,
    )
    num_ratings = models.IntegerField(
        default    = 0,
    )
    average_score = models.FloatField(
        default    = 0.0,
    )
    
    # ------------------------------------------------------------------------------
    # other functions and properties

    def __unicode__(self):
        return "%s.%s" % (self.namespace,self.name)

    def get_last_import(self):
        try:
            return model_to_dict(self.import_tasks.latest(), fields=('id', 'state'))
        except:
            return dict()

    def get_unique_platforms(self):
        return [platform.name for platform in self.platforms.filter(active=True).order_by('name').distinct('name')]

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
                    raise Exception("Role %s value exceeeds max length of %s." % (field.name, field.max_length))



class Namespace(PrimordialModel):

    class Meta:
        ordering = ('namespace',)

    namespace = models.CharField(
        max_length   = 256,
        unique       = True,
        verbose_name = "GitHub namespace"
    )
    name = models.CharField(
        max_length   = 256,
        blank        = True,
        null         = True,
        verbose_name = "GitHub name"
    )
    avatar_url = models.CharField(
        max_length   = 256,
        blank        = True,
        null         = True,
        verbose_name = "GitHub Avatar URL"
    )
    location = models.CharField(
        max_length   = 256,
        blank        = True,
        null         = True,
        verbose_name = "Location"
    )
    company = models.CharField(
        max_length   = 256,
        blank        = True,
        null         = True,
        verbose_name = "Location"
    )
    email = models.CharField(
        max_length   = 256,
        blank        = True,
        null         = True,
        verbose_name = "Location"
    )
    html_url = models.CharField(
        max_length   = 256,
        blank        = True,
        null         = True,
        verbose_name = "URL"
    )
    followers = models.IntegerField(
        null         = True,
        verbose_name  = "Followers"
    )


class RoleVersion(CommonModelNameNotUnique):
    class Meta:
        ordering = ('-loose_version',)

    #
    # ------------------------------------------------------------------------------
    # foreign keys

    role = models.ForeignKey(
        Role,
        related_name = 'versions',
    )

    #
    # ------------------------------------------------------------------------------
    # regular fields
    
    release_date = models.DateTimeField(
        blank      = True,
        null       = True,
    )
    loose_version = LooseVersionField(
        editable   = False,
        db_index   = True,
    )


    #
    # ------------------------------------------------------------------------------
    # other functions and properties

    def __unicode__(self):
        return "%s.%s-%s" % (self.role.namespace,self.role.name,self.name)

    def save(self, *args, **kwargs):
        # the value of score is based on the
        # values in the other rating fields
        self.loose_version = self.name
        super(RoleVersion, self).save(*args, **kwargs)

class RoleRating(PrimordialModel):

    class Meta:
        unique_together = ('owner','role')

    #
    # ------------------------------------------------------------------------------
    # foreign keys

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = 'ratings',
    )
    role = models.ForeignKey(
        Role,
        related_name = 'ratings',
    )

    #
    # ------------------------------------------------------------------------------
    # regular fields

    comment = models.TextField(
        blank      = True,
        null       = True,
    )
    score = models.IntegerField(
        default      = 0,
        db_index     = True,
    )

    #
    # ------------------------------------------------------------------------------
    # other functions and properties

    def __unicode__(self):
        return "%s.%s -> %s" % (self.role.namespace,self.role.name,self.score)

    def save(self, *args, **kwargs):
        def clamp_range(value):
            value = int(value)
            if value > 5:
                return 5
            elif value < 1:
                return 1
            else:
                return value
        
        self.score = clamp_range(self.score)
        
        if len(self.comment) > 5000:
            self.comment = self.comment[:5000]
        super(RoleRating, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.pk:
            return reverse('api:rating_detail', args=(self.pk,))
        else:
            return ""


class ImportTask(PrimordialModel):
    class Meta:
        ordering = ('-id',)
        get_latest_by = 'created'

    github_user = models.CharField(
        max_length   = 256,
        verbose_name = "Github Username",
    )
    github_repo = models.CharField(
        max_length   = 256,
        verbose_name = "Github Repository",
    )
    github_reference = models.CharField(
        max_length   = 256,
        verbose_name = "Github Reference",
        null         = True,
        blank        = True,
        default      = ''
    )
    role = models.ForeignKey(
        Role,
        related_name = 'import_tasks',
        db_index     = True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name  = 'import_tasks',
        db_index      = True,
    )
    alternate_role_name = models.CharField(
        max_length    = 256,
        verbose_name  = "Alternate Role Name",
        null          = True,
        blank         = True,
    )
    celery_task_id = models.CharField(
        max_length   = 100,
        blank        = True,
        null         = True,
    )
    state = models.CharField(
        max_length   = 20,
        default      = 'PENDING',
    )
    started = models.DateTimeField(
        auto_now_add = False,
        null         = True,
        blank        = True,
    )
    finished = models.DateTimeField(
        auto_now_add = False,
        null         = True,
        blank        = True,
    )

    # GitHub repo attributes at time of import
    stargazers_count = models.IntegerField(
        default      = 0
    )
    watchers_count   = models.IntegerField(
        default      = 0
    )
    forks_count      = models.IntegerField(
        default      = 0
    )
    open_issues_count = models.IntegerField(
        default      = 0
    )
    github_branch    = models.CharField(
        max_length = 256,
        blank = True,
        default = '',
        verbose_name = "Github Branch"
    )
    commit           = models.CharField(
        max_length   = 256,
        blank        = True
    )
    commit_message   = models.CharField(
        max_length   = 256,
        blank        = True
    )
    commit_url       = models.CharField(
        max_length   = 256,
        blank        = True
    )
    travis_status_url = models.CharField(
        max_length    = 256,
        blank         = True,
        default       = '',
        verbose_name  = "Travis Build Status"
    )
    travis_build_url  = models.CharField(
        max_length    = 256,
        blank         = True,
        default       = '',
        verbose_name  = "Travis Build URL"
    )

    def __unicode__(self):
        return "%d-%s" % (self.id,self.started.strftime("%Y%m%d-%H%M%S-%Z"))

    def validate_char_lengths(self):
        for field in self._meta.get_fields():
            if not field.is_relation and field.get_internal_type() == 'CharField':
                #print "%s %s" % (field.name, field.max_length)
                if isinstance(getattr(self, field.name), basestring) and len(getattr(self, field.name)) > field.max_length:
                    raise Exception("Import Task %s value exceeeds max length of %s." % (field.name, field.max_length))


class ImportTaskMessage(PrimordialModel):
    task = models.ForeignKey(
        ImportTask,
        related_name = 'messages',
    )
    message_type = models.CharField(
        max_length = 10,
    )
    message_text = models.CharField(
        max_length  = 256,
    )

    def __unicode__(self):
        return "%d-%s-%s" % (self.task.id,self.message_type,self.message_text)


class NotificationSecret(PrimordialModel):
    class Meta:
        ordering = ('source','github_user','github_repo')
        unique_together = ('source','github_user','github_repo')
        
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name  = 'notification_secrets',
        db_index      = True,
    )
    source = models.CharField(
        max_length    = 20,
        verbose_name  = "Source"
    )
    github_user = models.CharField(
        max_length   = 256,
        verbose_name = "Github Username",
    )
    github_repo = models.CharField(
        max_length   = 256,
        verbose_name = "Github Repository",
    )
    secret = models.CharField(
        max_length    = 256,
        verbose_name  = "Secret",
        db_index      = True
    )

    def __unicode__(self):
        return "%s-%s" % (self.owner.username,self.source)

    def repo_full_name(self):
        return "%s/%s" % (self.github_user, self.github_repo)


class Notification(PrimordialModel):
    class Meta:
        ordering = ('-id',)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name  = 'notifications',
        db_index      = True,
        editable      = False
    )
    source = models.CharField(
        max_length    = 20,
        verbose_name  = "Source",
        editable      = False
    )
    github_branch = models.CharField(
        max_length    = 256,
        verbose_name  = "GitHub Branch",
        blank         = True,
        editable      = False
    )
    travis_build_url = models.CharField(
        max_length   = 256,
        blank        = True
    )
    travis_status    = models.CharField(
        max_length   = 256,
        blank        = True
    )
    commit           = models.CharField(
        max_length   = 256,
        blank        = True
    )
    committed_at     = models.DateTimeField(
        auto_now     = False,
        null         = True
    )
    commit_message   = models.CharField(
        max_length   = 256,
        blank        = True
    )
    roles = models.ManyToManyField(
        Role,
        related_name  = 'notifications',
        verbose_name  = 'Roles',
        editable      = False
    )
    imports = models.ManyToManyField(
        ImportTask,
        related_name  = 'notifications',
        verbose_name  = 'Tasks',
        editable      = False
    )
    messages = ArrayField(
        models.CharField(max_length=256),
        default       = list,
        editable      = False
    )


class Repository (PrimordialModel):
    class Meta:
        unique_together = ('owner', 'github_user', 'github_repo')
        ordering = ('github_user','github_repo')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name  = 'repositories',
    )
    github_user = models.CharField(
        max_length   = 256,
        verbose_name = "Github Username",
    )
    github_repo = models.CharField(
        max_length   = 256,
        verbose_name = "Github Repository",
    )
    is_enabled = models.BooleanField(
        default      = False
    )


class Subscription (PrimordialModel):
    class Meta:
        unique_together = ('owner','github_user','github_repo')
        ordering = ('owner', 'github_user', 'github_repo')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name   = 'subscriptions',
    )
    github_user = models.CharField(
        max_length     = 256,
        verbose_name   = "Github Username",
    )
    github_repo = models.CharField(
        max_length     = 256,
        verbose_name   = "Github Repository",
    )


class Stargazer (PrimordialModel):
    class Meta:
        unique_together = ('owner','github_user','github_repo')
        ordering = ('owner', 'github_user', 'github_repo')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = 'starred',
    )
    github_user = models.CharField(
        max_length   = 256,
        verbose_name = "Github Username",
    )
    github_repo = models.CharField(
        max_length   = 256,
        verbose_name = "Github Repository",
    )


class RefreshRoleCount (PrimordialModel):
    state = models.CharField(
        max_length   = 20
    )
    passed = models.IntegerField(
        default      = 0,
        null         = True
    )
    failed = models.IntegerField(
        default      = 0,
        null         = True
    )
    deleted = models.IntegerField(
        default      = 0,
        null         = True
    )
    skipped = models.IntegerField(
        default      = 0,
        null         = True
    )


