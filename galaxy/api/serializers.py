# (c) 2012-2014, Ansible, Inc. <support@ansible.com>
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

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
                                Category,
                                Tag,
                                Role,
                                ImportTask,
                                RoleVersion,
                                NotificationSecret,
                                Notification,
                                Repository,
                                Subscription,
                                Stargazer)

# rst2html5-tools
from html5css3 import Writer
from docutils.core import publish_string

User = get_user_model()

BASE_FIELDS = ('id', 'url', 'related', 'summary_fields', 'created', 'modified', 'name')

# Fields that should be summarized regardless of object type.
DEFAULT_SUMMARY_FIELDS = ('name', 'description',)

SUMMARIZABLE_FK_FIELDS = {
    'owner' : ('id','url','username', 'full_name', 'avatar_url'),
    'role'  : ('id','url','name',),
}


def readme_to_html(obj):
    if obj is None or obj.readme is None:
        return ''
    if obj.readme_type is None or obj.readme_type == 'md':
        return markdown.markdown(html_decode(obj.readme), extensions=['extra'])
    if obj.readme_type == 'rst':
        settings = {'input_encoding': 'utf8'}
        return publish_string(
            source=obj.readme,
            writer=Writer(),
            writer_name='html5css3',
            settings_overrides=settings,
        ).decode('utf8')


class BaseSerializer(serializers.ModelSerializer):
    # add the URL and related resources
    url            = serializers.SerializerMethodField()
    related        = serializers.SerializerMethodField()
    summary_fields = serializers.SerializerMethodField()

    # make certain fields read only
    created       = serializers.SerializerMethodField()
    modified      = serializers.SerializerMethodField()
    active        = serializers.SerializerMethodField()

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
            return obj.last_login # Not actually exposed for User.
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
        fields = ('id','authenticated','staff','username',)

    def get_summary_fields(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        d = super(MeSerializer, self).get_summary_fields(obj)
        return d


class UserListSerializer(BaseSerializer):
    staff          = serializers.ReadOnlyField(source='is_staff')
    email          = serializers.SerializerMethodField()

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
            subscriptions = reverse('api:user_subscription_list', args=(obj.pk,)),
            starred = reverse('api:user_starred_list', args=(obj.pk,)),
            repositories = reverse('api:user_repositories_list', args=(obj.pk,)),
            secrets = reverse('api:user_notification_secret_list', args=(obj.pk,)),
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
                ('github_user', g.github_user),
                ('github_repo', g.github_repo)
            ]) for g in obj.starred.all()]
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
    staff          = serializers.ReadOnlyField(source='is_staff')
    email          = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'email','karma',
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
            repositories = reverse('api:user_repositories_list', args=(obj.pk,)),
            subscriptions = reverse('api:user_subscription_list', args=(obj.pk,)),
            starred = reverse('api:user_starred_list', args=(obj.pk,)),
            secrets = reverse('api:user_notification_secret_list', args=(obj.pk,)),
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
                ('github_user', g.github_user),
                ('github_repo', g.github_repo)
            ]) for g in obj.starred.all()]
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


class StargazerSerializer(BaseSerializer):
    owner = serializers.CharField(read_only=True)

    class Meta:
        model = Stargazer
        fields = ('owner', 'github_user', 'github_repo')

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


class RoleVersionSerializer(BaseSerializer):
    class Meta:
        model = RoleVersion
        fields = ('id','name','release_date',)


class RepositorySerializer(BaseSerializer):
    class Meta:
        model = Repository
        fields = ('id', 'owner', 'github_user', 'github_repo', 'is_enabled')

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Repository):
            return reverse('api:repository_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(RepositorySerializer, self).get_related(obj)
        res.update(dict(
            owner = reverse('api:user_detail', args=(obj.owner.id,)),
        ))
        return res

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(RepositorySerializer, self).get_summary_fields(obj)
        d['notification_secrets'] = [
            OrderedDict([
                ('id',s.id),
                ('github_user',s.github_user),
                ('github_repo',s.github_repo),
                ('source',s.source),
                ('secret','******' + s.secret[-4:]),
            ]) for s in NotificationSecret.objects.filter(github_user=obj.github_user, github_repo=obj.github_repo)
        ]
        d['roles'] = [
            OrderedDict([
                ('id', r.id),
                ('namespace', r.namespace),
                ('name', r.name)
            ]) for r in Role.objects.filter(github_user=obj.github_user, github_repo=obj.github_repo)
        ]
        return d


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
            roles = reverse('api:notification_roles_list', args=(obj.pk,)),
            imports = reverse('api:notification_imports_list', args=(obj.pk,)),
            owner = reverse('api:user_detail', args=(obj.owner.id,)),
        ))
        return res


class ImportTaskSerializer(BaseSerializer):
    class Meta:
        model = ImportTask
        fields = (
            'id',
            'github_user',
            'github_repo',
            'github_reference',
            'github_branch',
            'role',
            'owner',
            'alternate_role_name',
            'celery_task_id',
            'state',
            'started',
            'finished',
            'modified',
            'created',
            'active',
            'stargazers_count', 
            'watchers_count',
            'forks_count',
            'open_issues_count',
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
            role=reverse('api:role_detail', args=(obj.role_id,)),
            notifications=reverse('api:import_task_notification_list', args=(obj.pk,)),
        ))
        return res

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(ImportTaskSerializer, self).get_summary_fields(obj)
        d['role'] = OrderedDict([
            ('id',obj.role.id),
            ('namespace',obj.role.namespace),
            ('name',obj.role.name),
            ('is_valid', obj.role.is_valid),
            ('active', obj.role.active),
        ])
        
        d['notifications'] = [OrderedDict([
            ('id', n.id),
            ('travis_build_url', n.travis_build_url),
            ('commit_message', n.commit_message),
            ('committed_at', n.committed_at),
            ('commit', n.commit)
        ]) for n in obj.notifications.all().order_by('id')]

        d['task_messages'] = [OrderedDict([
            ('id',g.id),
            ('message_type',g.message_type),
            ('message_text',g.message_text)
        ]) for g in obj.messages.all().order_by('id')]
        return d


class ImportTaskLatestSerializer(BaseSerializer):
    id = serializers.SerializerMethodField()
    owner_id = serializers.SerializerMethodField()

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
        r = Role.objects.get(id=g.role.id)
        d['details'] = OrderedDict([
            ('id', g.id),
            ('state', g.state),
            ('github_user', g.github_user),
            ('github_repo', g.github_repo),
            ('github_reference', g.github_reference),
            ('github_branch', g.github_branch),
            ('role', g.role.id),
            ('modified', g.modified),
            ('created', g.created),
            ('stargazers_count', g.stargazers_count),
            ('watchers_count', g.watchers_count),
            ('forks_count', g.forks_count),
            ('open_issues_count', g.open_issues_count),
            ('commit', g.commit),
            ('commit_message', g.commit_message),
            ('commit_url', g.commit_url)
        ])
        d['role'] = OrderedDict([
            ('id',r.id),
            ('is_valid', r.is_valid),
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


class RoleListSerializer(BaseSerializer):
    readme_html = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = BASE_FIELDS + ('namespace', 'is_valid','github_user', 'github_repo',
                                'github_branch', 'min_ansible_version', 'issue_tracker_url',
                                'license','company', 'description', 'readme_html',
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
        elif isinstance(obj, Role):
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
            dict(id=g.id,
                 name=g.name,
                 release_date=g.release_date) for g in obj.versions.all()]
        return d

    def get_readme_html(self, obj):
        return readme_to_html(obj)


class RoleTopSerializer(BaseSerializer):

    class Meta:
        model = Role
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
            dependencies = reverse('api:role_dependencies_list', args=(obj.pk,)),
            imports  = reverse('api:role_import_task_list', args=(obj.pk,)),
            versions = reverse('api:role_versions_list', args=(obj.pk,)),
        ))
        return res

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Role):
            return reverse('api:role_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()


class RoleDetailSerializer(BaseSerializer):
    readme_html          = serializers.SerializerMethodField()
    tags                 = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = BASE_FIELDS + ('namespace','is_valid','github_user','github_repo','github_branch','min_ansible_version',
                                'issue_tracker_url', 'license','company','description','readme_html', 'tags',
                                'travis_status_url', 'stargazers_count', 'watchers_count', 'forks_count',
                                'open_issues_count', 'commit', 'commit_message','commit_url', 'created', 'modified',
                                'download_count','imported')

    def to_native(self, obj):
        ret = super(RoleDetailSerializer, self).to_native(obj)
        return ret

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(RoleDetailSerializer, self).get_related(obj)
        res.update(dict(
            dependencies = reverse('api:role_dependencies_list', args=(obj.pk,)),
            imports  = reverse('api:role_import_task_list', args=(obj.pk,)),
            versions = reverse('api:role_versions_list', args=(obj.pk,)),
        ))
        return res

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Role):
            return reverse('api:role_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()

    def get_tags(self, obj):
        return [t for t in obj.get_tags()]

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(RoleDetailSerializer, self).get_summary_fields(obj)
        d['dependencies'] = [
            dict(id=g.id, name=str(g)) for g in obj.dependencies.all()]
        d['platforms'] = [
            dict(name=g.name, release=g.release) for g in obj.platforms.all()]
        d['tags'] = [
            dict(name=g.name) for g in obj.tags.all()]
        d['versions'] = [
            dict(id=g.id, name=g.name, release_date=g.release_date) for g in obj.versions.all()]
        return d
    
    def get_readme_html(self, obj):
        return readme_to_html(obj)


class RoleSearchSerializer(HaystackSerializer):
    platforms = serializers.SerializerMethodField()
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
            "username",
            "name", 
            "description", 
            "github_user",
            "github_repo",
            "github_branch",
            "tags",
            "platforms",
            "platform_details", 
            "versions",
            "dependencies",
            "created", 
            "modified",
            "imported",
            "text",
            "autocomplete",
            "platforms_autocomplete",
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
        return [p for p in instance.platforms]

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
                Subscription.objects.get(owner=request.user,github_user=instance.github_user, github_repo=instance.github_repo)
                return True
            except:
                pass
        return False

    def get_user_is_stargazer(self, instance):
        # override user_is_stargazer found in ES
        request = self.context.get('request', None)
        if request is not None:
            try:
                Stargazer.objects.get(owner=request.user,github_user=instance.github_user, github_repo=instance.github_repo)
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
                if hasattr(obj[key],'__iter__'):
                    result[key] = [itm for itm in obj[key]]
                else:
                    result[key] = obj[key]
        return result
