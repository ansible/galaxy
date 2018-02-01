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

import markdown
import json

from rest_framework import serializers

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from collections import OrderedDict


# haystack
from drf_haystack.serializers import HaystackSerializer

# galaxy
from galaxy.main.search_indexes import RoleIndex
from galaxy.api.utils import html_decode
from galaxy.main.models import (Platform,
                                CloudPlatform,
                                Category,
                                Tag,
                                Content,
                                ImportTask,
                                ContentVersion,
                                Namespace,
                                NotificationSecret,
                                Notification,
                                Provider,
                                Repository,
                                Subscription,
                                Stargazer
                                )

# rst2html5-tools
from html5css3 import Writer
from docutils.core import publish_string

__all__ = [
    'BaseSerializer',
    'MeSerializer',
    'UserListSerializer',
    'UserDetailSerializer',
    'SubscriptionSerializer',
    'StargazerSerializer',
    'CategorySerializer',
    'TagSerializer',
    'PlatformSerializer',
    'RoleVersionSerializer',
    'RepositorySerializer',
    'TopContributorsSerializer',
    'NamespaceSerializer',
    'NotificationSecretSerializer',
    'NotificationSerializer',
    'ImportTaskSerializer',
    'ImportTaskLatestSerializer',
    'ProviderSerializer',
    'RoleListSerializer',
    'RoleTopSerializer',
    'RoleDetailSerializer',
    'RoleSearchSerializer',
    'ElasticSearchDSLSerializer'
]


User = get_user_model()

BASE_FIELDS = ('id', 'url', 'related', 'summary_fields', 'created', 'modified', 'name')

# Fields that should be summarized regardless of object type.
DEFAULT_SUMMARY_FIELDS = ('name', 'description',)

SUMMARIZABLE_FK_FIELDS = {
    'owner': ('id', 'url', 'username', 'full_name', 'avatar_url'),
    'role': ('id', 'url', 'name',),
}


def readme_to_html(obj):
    if obj is None or obj.readme is None:
        return ''
    content = ''
    if obj.readme_type is None or obj.readme_type == 'md':
        try:
            content = markdown.markdown(html_decode(obj.readme), extensions=['extra'])
        except:
            content = "Failed to convert README to HTML. Galaxy now stores the GitHub generated HTML for your " \
                      "README. If you re-import this role, the HTML will show up, and this message will go away."

    if obj.readme_type == 'rst':
        settings = {'input_encoding': 'utf8'}
        try:
            content = publish_string(
                source=obj.readme,
                writer=Writer(),
                writer_name='html5css3',
                settings_overrides=settings,
            ).decode('utf8')
        except:
            content = "Failed to convert README to HTML. Galaxy now stores the GitHub generated HTML for your " \
                      "README. If you re-import this role, the HTML will show up, and this message will go away."

    return content


class BaseSerializer(serializers.ModelSerializer):
    # add the URL and related resources
    url = serializers.SerializerMethodField()
    related = serializers.SerializerMethodField()
    summary_fields = serializers.SerializerMethodField()

    # make certain fields read only
    created = serializers.SerializerMethodField()
    modified = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(BaseSerializer, self).__init__(*args, **kwargs)
        self.Meta.fields = ('url', 'related', 'summary_fields') + self.Meta.fields + ('created', 'modified', 'active')

    def get_fields(self):
        # opts = get_concrete_model(self.Meta.model)._meta
        opts = self.Meta.model._meta.concrete_model._meta
        ret = super(BaseSerializer, self).get_fields()
        for key, field in ret.items():
            if key == 'id' and not getattr(field, 'help_text', None):
                field.help_text = 'Database ID for this %s.' % unicode(opts.verbose_name)
            elif key == 'url':
                field.help_text = 'URL for this %s.' % unicode(opts.verbose_name)
                field.type_label = 'string'
            elif key == 'related':
                field.help_text = 'Data structure with URLs of related resources.'
                field.type_label = 'object'
            elif key == 'summary_fields':
                field.help_text = 'Data structure with name/description for related resources.'
                field.type_label = 'object'
            elif key == 'created':
                field.help_text = 'Timestamp when this %s was created.' % unicode(opts.verbose_name)
                field.type_label = 'datetime'
            elif key == 'modified':
                field.help_text = 'Timestamp when this %s was last modified.' % unicode(opts.verbose_name)
                field.type_label = 'datetime'
        return ret

    def get_url(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return ''
        elif isinstance(obj, User):
            return reverse('api:user_detail', args=(obj.pk,))
        else:
            try:
                return obj.get_absolute_url()
            except AttributeError:
                return ''

    def get_related(self, obj):
        res = OrderedDict()
        if getattr(obj, 'owner', None):
            res['owner'] = reverse('api:user_detail', args=(obj.owner.pk,))
        return res

    def get_summary_fields(self, obj):
        # Return values for certain fields on related objects, to simplify
        # displaying lists of items without additional API requests.
        summary_fields = dict()
        for fk, related_fields in SUMMARIZABLE_FK_FIELDS.items():
            try:
                fkval = getattr(obj, fk, None)
                if fkval is not None:
                    summary_fields[fk] = dict()
                    for field in related_fields:
                        fval = getattr(fkval, field, None)
                        if fval is not None:
                            summary_fields[fk][field] = fval
            # Can be raised by the reverse accessor for a OneToOneField.
            except ObjectDoesNotExist:
                pass
        return summary_fields

    def get_created(self, obj):
        if obj is None:
            return None
        elif isinstance(obj, User):
            return obj.date_joined
        else:
            try:
                return obj.created
            except AttributeError:
                return None

    def get_modified(self, obj):
        if obj is None:
            return None
        elif isinstance(obj, User):
            return obj.last_login  # Not actually exposed for User.
        else:
            try:
                return obj.modified
            except AttributeError:
                return None

    def get_active(self, obj):
        if obj is None:
            return False
        elif isinstance(obj, User):
            return obj.is_active
        else:
            try:
                return obj.active
            except AttributeError:
                return None

    def validate_description(self, attrs, source):
        # Description should always be empty string, never null.
        attrs[source] = attrs.get(source, None) or ''
        return attrs


class MeSerializer(BaseSerializer):
    authenticated = serializers.ReadOnlyField(source='is_authenticated')
    staff = serializers.ReadOnlyField(source='is_staff')

    class Meta:
        model = User
        fields = ('id', 'authenticated', 'staff', 'username',)

    def get_summary_fields(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        d = super(MeSerializer, self).get_summary_fields(obj)
        return d


class UserListSerializer(BaseSerializer):
    staff = serializers.ReadOnlyField(source='is_staff')
    email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'staff',
            'full_name',
            'date_joined',
            'github_avatar',
            'github_user',
            'cache_refreshed'
        )

    def get_related(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        res = super(UserListSerializer, self).get_related(obj)
        res.update(dict(
            subscriptions=reverse('api:user_subscription_list', args=(obj.pk,)),
            starred=reverse('api:user_starred_list', args=(obj.pk,)),
            repositories=reverse('api:user_repositories_list', args=(obj.pk,)),
            secrets=reverse('api:user_notification_secret_list', args=(obj.pk,)),
        ))
        return res

    def get_summary_fields(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        d = super(UserListSerializer, self).get_summary_fields(obj)
        d['subscriptions'] = [
            OrderedDict([
                ('id', g.id),
                ('github_user', g.github_user),
                ('github_repo', g.github_repo)
            ]) for g in obj.subscriptions.all()]
        d['starred'] = [
            OrderedDict([
                ('id', g.id),
                ('github_user', g.repository.github_user),
                ('github_repo', g.repository.github_repo)
            ]) for g in obj.starred.select_related('repository').all()]
        return d

    def get_email(self, obj):
        if self.context['request'].user.is_staff:
            return obj.email
        else:
            return ''


class UserDetailSerializer(BaseSerializer):
    password = serializers.CharField(
        required=False,
        write_only=True,
        default='',
        help_text='Write-only field used to change the password.'
    )
    staff = serializers.ReadOnlyField(source='is_staff')
    email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'email', 'karma',
            'staff',
            'full_name',
            'date_joined',
            'github_avatar',
            'github_user',
            'cache_refreshed'
        )

    def to_native(self, obj):
        ret = super(UserDetailSerializer, self).to_native(obj)
        ret.pop('password', None)
        ret.fields.pop('password', None)
        return ret

    def get_validation_exclusions(self):
        ret = super(UserDetailSerializer, self).get_validation_exclusions()
        ret.append('password')
        return ret

    def restore_object(self, attrs, instance=None):
        new_password = attrs.pop('password', None)
        instance = super(UserDetailSerializer, self).restore_object(attrs, instance)
        instance._new_password = new_password
        return instance

    def save_object(self, obj, **kwargs):
        new_password = getattr(obj, '_new_password', None)
        if new_password:
            obj.set_password(new_password)
        if not obj.password:
            obj.set_unusable_password()
        return super(UserDetailSerializer, self).save_object(obj, **kwargs)

    def get_related(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        res = super(UserDetailSerializer, self).get_related(obj)
        res.update(dict(
            repositories=reverse('api:user_repositories_list', args=(obj.pk,)),
            subscriptions=reverse('api:user_subscription_list', args=(obj.pk,)),
            starred=reverse('api:user_starred_list', args=(obj.pk,)),
            secrets=reverse('api:user_notification_secret_list', args=(obj.pk,)),
        ))
        return res

    def get_summary_fields(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        d = super(UserDetailSerializer, self).get_summary_fields(obj)
        d['subscriptions'] = [
            OrderedDict([
                ('id', g.id),
                ('github_user', g.github_user),
                ('github_repo', g.github_repo)
            ]) for g in obj.subscriptions.all()]
        d['starred'] = [
            OrderedDict([
                ('id', g.id),
                ('github_user', g.repository.github_user),
                ('github_repo', g.repository.github_repo)
            ]) for g in obj.starred.select_related('repository').all()]
        return d

    def get_email(self, obj):
        if self.context['request'].user.is_staff:
            return obj.email
        else:
            return ''


class SubscriptionSerializer(BaseSerializer):
    owner = serializers.CharField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('owner', 'github_user', 'github_repo')

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Subscription):
            return reverse('api:subscription_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()


class StargazerRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ('id', 'namespace', 'name', 'github_repo', 'github_user')


class StargazerSerializer(BaseSerializer):
    owner = serializers.CharField(read_only=True)
    role = StargazerRoleSerializer(read_only=True)

    class Meta:
        model = Stargazer
        fields = ('owner', 'role')

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Stargazer):
            return reverse('api:stargazer_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()


class CategorySerializer(BaseSerializer):
    class Meta:
        model = Category
        fields = BASE_FIELDS


class TagSerializer(BaseSerializer):
    class Meta:
        model = Tag
        fields = BASE_FIELDS


class PlatformSerializer(BaseSerializer):
    class Meta:
        model = Platform
        fields = BASE_FIELDS + ('release',)


class CloudPlatformSerializer(BaseSerializer):
    class Meta:
        model = CloudPlatform
        fields = BASE_FIELDS


class RoleVersionSerializer(BaseSerializer):
    class Meta:
        model = ContentVersion
        fields = ('id', 'name', 'release_date',)


class RepositorySerializer(BaseSerializer):
    github_user = serializers.SerializerMethodField()
    github_repo = serializers.SerializerMethodField()

    class Meta:
        model = Repository
        fields = ('id', 'owners', 'github_user', 'github_repo', 'is_enabled')

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Repository):
            return reverse('api:repository_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(RepositorySerializer, self).get_summary_fields(obj)
        d['notification_secrets'] = [
            OrderedDict([
                ('id', s.id),
                ('github_user', s.github_user),
                ('github_repo', s.github_repo),
                ('source', s.source),
                ('secret', '******' + s.secret[-4:]),
            ]) for s in NotificationSecret.objects.filter(
                github_user=obj.github_user,
                github_repo=obj.github_repo)
        ]
        d['roles'] = [
            OrderedDict([
                ('id', r.id),
                ('namespace', r.namespace.name),
                ('name', r.name),
                ('last_import', dict())
            ]) for r in Content.objects.filter(repository=obj)
        ]
        for role in d['roles']:
            tasks = list(
                ImportTask.objects.filter(repository=obj)
                .order_by('-id'))
            if len(tasks) > 0:
                role['last_import']['id'] = tasks[0].id
                role['last_import']['state'] = tasks[0].state
        return d

    def get_github_user(self, obj):
        return obj.provider_namespace.name

    def get_github_repo(self, obj):
        return obj.name


class TopContributorsSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):
        return {
            'namespace': obj['namespace'],
            'role_count': obj['count']
        }


class NotificationSecretSerializer(BaseSerializer):
    secret = serializers.SerializerMethodField()

    class Meta:
        model = NotificationSecret
        fields = (
            'id',
            'owner',
            'github_user',
            'github_repo',
            'source',
            'secret',
            'created',
            'modified',
            'active'
        )

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, NotificationSecret):
            return reverse('api:notification_secret_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()

    def get_secret(self, obj):
        # show only last 4 digits of secret
        last = ''
        try:
            last = obj.secret[-4:]
        except:
            pass
        return '******' + last


class NotificationSerializer(BaseSerializer):
    class Meta:
        model = Notification
        fields = (
            'id',
            'owner',
            'source',
            'github_branch',
            'travis_build_url',
            'travis_status',
            'commit_message',
            'committed_at',
            'commit',
            'messages',
            'created',
            'modified'
        )

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Notification):
            return reverse('api:notification_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(NotificationSerializer, self).get_summary_fields(obj)
        d['owner'] = OrderedDict([
            ('id', obj.owner.id),
            ('username', obj.owner.username)
        ])
        d['roles'] = [OrderedDict([
            ('id', r.id),
            ('namespace', r.namespace),
            ('name', r.name)
        ]) for r in obj.roles.all()]
        d['imports'] = [OrderedDict([
            ('id', t.id)
        ]) for t in obj.imports.all()]
        return d

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(NotificationSerializer, self).get_related(obj)
        res.update(dict(
            roles=reverse('api:notification_roles_list', args=(obj.pk,)),
            imports=reverse('api:notification_imports_list', args=(obj.pk,)),
            owner=reverse('api:user_detail', args=(obj.owner.id,)),
        ))
        return res


class ImportTaskSerializer(BaseSerializer):
    github_user = serializers.SerializerMethodField()
    github_repo = serializers.SerializerMethodField()

    class Meta:
        model = ImportTask
        fields = (
            'id',
            'github_reference',
            'github_user',
            'github_repo',
            'repository',
            'owner',
            'alternate_role_name',
            'celery_task_id',
            'state',
            'started',
            'finished',
            'modified',
            'created',
            'active',
            'commit',
            'commit_message',
            'commit_url',
            'travis_status_url',
            'travis_build_url'
        )

    def to_native(self, obj):
        ret = super(ImportTaskSerializer, self).to_native(obj)
        return ret

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, ImportTask):
            return reverse('api:import_task_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(ImportTaskSerializer, self).get_related(obj)
        res.update(dict(
            role=reverse('api:repository_detail', args=(obj.repository_id,)),
            notifications=reverse('api:import_task_notification_list', args=(obj.pk,)),
        ))
        return res

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(ImportTaskSerializer, self).get_summary_fields(obj)
        d['notifications'] = [OrderedDict([
            ('id', n.id),
            ('travis_build_url', n.travis_build_url),
            ('commit_message', n.commit_message),
            ('committed_at', n.committed_at),
            ('commit', n.commit)
        ]) for n in obj.notifications.all().order_by('id')]

        d['task_messages'] = [OrderedDict([
            ('id', g.id),
            ('message_type', g.message_type),
            ('message_text', g.message_text)
        ]) for g in obj.messages.all().order_by('id')]
        return d

    def get_github_user(self, obj):
        return obj.repository.github_user

    def get_github_repo(self, obj):
        return obj.repository.github_repo


class ImportTaskLatestSerializer(BaseSerializer):
    id = serializers.SerializerMethodField()
    owner_id = serializers.SerializerMethodField()
    github_user = serializers.SerializerMethodField()
    github_repo = serializers.SerializerMethodField()

    class Meta:
        model = ImportTask
        fields = (
            'id',
            'owner_id',
            'github_user',
            'github_repo',
        )

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(ImportTaskLatestSerializer, self).get_summary_fields(obj)
        g = ImportTask.objects.get(id=obj['last_id'])
        d['details'] = OrderedDict([
            ('id', g.id),
            ('state', g.state),
            ('github_user', g.repository.github_user),
            ('github_repo', g.repository.github_repo),
            ('github_reference', g.github_reference),
            ('modified', g.modified),
            ('created', g.created),
        ])
        return d

    def get_url(self, obj):
        if obj is None:
            return ''
        else:
            return reverse('api:import_task_detail', args=(obj['last_id'],))

    def get_id(self, obj):
        return obj['last_id']

    def get_owner_id(self, obj):
        return obj['owner_id']

    def get_github_user(self, obj):
        return obj['repository__provider_namespace__name']

    def get_github_repo(self, obj):
        return obj['repository__name']


class RoleListSerializer(BaseSerializer):
    readme_html = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = BASE_FIELDS + ('role_type', 'namespace', 'is_valid', 'github_user', 'github_repo',
                                'github_branch', 'min_ansible_version', 'issue_tracker_url',
                                'license', 'company', 'description', 'readme', 'readme_html',
                                'travis_status_url', 'stargazers_count', 'watchers_count',
                                'forks_count', 'open_issues_count', 'commit', 'commit_message',
                                'commit_url', 'download_count')

    def to_native(self, obj):
        ret = super(RoleListSerializer, self).to_native(obj)
        return ret

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(RoleListSerializer, self).get_related(obj)
        res.update(dict(
            dependencies=reverse('api:role_dependencies_list', args=(obj.pk,)),
            imports=reverse('api:role_import_task_list', args=(obj.pk,)),
            versions=reverse('api:role_versions_list', args=(obj.pk,)),
            notifications=reverse('api:role_notification_list', args=(obj.pk,)),
        ))
        return res

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Content):
            return reverse('api:role_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(RoleListSerializer, self).get_summary_fields(obj)
        d['dependencies'] = [str(g) for g in obj.dependencies.all()]
        d['platforms'] = [
            dict(name=g.name, release=g.release) for g in obj.platforms.all()]
        d['tags'] = [
            dict(name=g.name) for g in obj.tags.all()]
        d['versions'] = [
            dict(id=g.id, name=g.name, release_date=g.release_date) for g in obj.versions.all()]
        d['videos'] = [dict(url=v.url, description=v.description) for v in obj.videos.all()]
        return d

    def get_readme_html(self, obj):
        if obj.readme_html:
            return obj.readme_html
        return readme_to_html(obj)


class RoleTopSerializer(BaseSerializer):

    class Meta:
        model = Content
        fields = BASE_FIELDS + ('github_user',
                                'github_repo',
                                'min_ansible_version',
                                'issue_tracker_url',
                                'license',
                                'company',
                                'description')

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(RoleTopSerializer, self).get_related(obj)
        res.update(dict(
            dependencies=reverse('api:role_dependencies_list', args=(obj.pk,)),
            imports=reverse('api:role_import_task_list', args=(obj.pk,)),
            versions=reverse('api:role_versions_list', args=(obj.pk,)),
        ))
        return res

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Content):
            return reverse('api:role_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()


class RoleDetailSerializer(BaseSerializer):
    readme_html = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = BASE_FIELDS + ('role_type', 'namespace', 'is_valid', 'github_user', 'github_repo', 'github_branch',
                                'min_ansible_version', 'issue_tracker_url', 'license', 'company', 'description',
                                'readme', 'readme_html', 'tags', 'travis_status_url', 'stargazers_count',
                                'watchers_count', 'forks_count', 'open_issues_count', 'commit', 'commit_message',
                                'commit_url', 'created', 'modified', 'download_count', 'imported')

    def to_native(self, obj):
        ret = super(RoleDetailSerializer, self).to_native(obj)
        return ret

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(RoleDetailSerializer, self).get_related(obj)
        res.update(dict(
            dependencies=reverse('api:role_dependencies_list', args=(obj.pk,)),
            imports=reverse('api:role_import_task_list', args=(obj.pk,)),
            versions=reverse('api:role_versions_list', args=(obj.pk,)),
        ))
        return res

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Content):
            return reverse('api:role_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()

    def get_tags(self, obj):
        return [t for t in obj.get_tags()]

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(RoleDetailSerializer, self).get_summary_fields(obj)
        d['dependencies'] = [dict(id=g.id, name=str(g)) for g in obj.dependencies.all()]
        d['platforms'] = [dict(name=g.name, release=g.release) for g in obj.platforms.all()]
        d['tags'] = [dict(name=g.name) for g in obj.tags.all()]
        d['versions'] = [dict(id=g.id, name=g.name, release_date=g.release_date) for g in obj.versions.all()]
        d['videos'] = [dict(url=v.url, description=v.description) for v in obj.videos.all()]
        return d

    def get_readme_html(self, obj):
        if obj.readme_html:
            return obj.readme_html
        return readme_to_html(obj)


class RoleSearchSerializer(HaystackSerializer):
    platforms = serializers.SerializerMethodField()
    cloud_platforms = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    versions = serializers.SerializerMethodField()
    dependencies = serializers.SerializerMethodField()
    platform_details = serializers.SerializerMethodField()
    user_is_subscriber = serializers.SerializerMethodField()
    user_is_stargazer = serializers.SerializerMethodField()

    class Meta:
        index_classes = [RoleIndex]
        fields = (
            "role_id",
            "role_type",
            "username",
            "name",
            "description",
            "github_user",
            "github_repo",
            "github_branch",
            "tags",
            "platforms",
            "cloud_platforms",
            "platform_details",
            "versions",
            "dependencies",
            "created",
            "modified",
            "imported",
            "last_commit_date",
            "text",
            "autocomplete",
            "platforms_autocomplete",
            "cloud_platforms_autocomplete",
            "tags_autocomplete",
            "username_autocomplete",
            "travis_status_url",
            "travis_build_url",
            "issue_tracker_url",
            "stargazers_count",
            "watchers_count",
            "forks_count",
            "open_issues_count",
            "min_ansible_version",
            "user_is_stargazer",
            "user_is_subscriber",
            "download_count",
        )

    def to_representation(self, instance):
        ''' Show field in the order listed above. '''
        rep = super(RoleSearchSerializer, self).to_representation(instance)
        result = OrderedDict()
        for fld in self.Meta.fields:
            result[fld] = rep[fld]
        return result

    def get_platforms(self, instance):
        if instance is None:
            return []
        # FIXME(cutwater): List comprehension is redundant
        return [p for p in instance.platforms]

    def get_cloud_platforms(self, instance):
        return instance.cloud_platforms or []

    def get_tags(self, instance):
        if instance is None:
            return []
        return [t for t in instance.tags]

    def get_versions(self, instance):
        if instance is None:
            return []
        return json.loads(instance.versions)

    def get_dependencies(self, instance):
        if instance is None:
            return []
        return json.loads(instance.dependencies)

    def get_platform_details(self, instance):
        if instance is None:
            return []
        return json.loads(instance.platform_details)

    def get_user_is_subscriber(self, instance):
        # override user_is_subscriber found in ES
        request = self.context.get('request', None)
        if request is not None and request.user.is_authenticated():
            try:
                Subscription.objects.get(owner=request.user, github_user=instance.github_user, github_repo=instance.github_repo)
                return True
            except:
                pass
        return False

    def get_user_is_stargazer(self, instance):
        # override user_is_stargazer found in ES
        request = self.context.get('request', None)
        if request is not None:
            try:
                Stargazer.objects.get(
                    owner=request.user,
                    role=instance)
                return True
            except:
                pass
        return False


class ElasticSearchDSLSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        result = OrderedDict()
        result['score'] = obj.meta.score
        result['type'] = obj.meta.doc_type
        result['id'] = obj.meta.id
        for key in obj:
            if key != 'meta':
                if hasattr(obj[key], '__iter__'):
                    result[key] = [itm for itm in obj[key]]
                else:
                    result[key] = obj[key]
        return result


class NamespaceSerializer(BaseSerializer):

    class Meta:
        model = Namespace
        fields = (
            'id',
            'name',
            'description',
            'avatar_url',
            'location',
            'company',
            'email',
            'html_url',
        )

    def get_summary_fields(self, instance):
        owners = [{
            'id': u.id,
            'github_user': u.github_user,
            'github_avatar': u.github_avatar,
            'username': u.username
        } for u in instance.owners.all()]
        provider_namespaces = [{
            'id': pn.id,
            'name': pn.name,
            'display_name': pn.display_name,
            'avatar_url': pn.avatar_url,
            'location': pn.location,
            'compay': pn.company,
            'description': pn.description,
            'email': pn.email,
            'html_url': pn.html_url,
            'provider': pn.provider.name,
        } for pn in instance.provider_namespaces.all()]
        return {
            'owners': owners,
            'provider_namespaces': provider_namespaces
        }


class ProviderSerializer(BaseSerializer):

    class Meta:
        model = Provider
        fields = (
            'id',
            'name',
            'original_name',
            'description',
        )

    def get_url(self, obj):
        return reverse('api:active_provider_detail', args=(obj.pk,)) if obj else ''
