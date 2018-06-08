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

from rest_framework import serializers

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from collections import OrderedDict


from galaxy.main.models import (Platform,
                                CloudPlatform,
                                Category,
                                Tag,
                                Content,
                                ImportTask,
                                RepositoryVersion,
                                Subscription,
                                Stargazer
                                )

__all__ = [
    'BaseSerializer',
    'MeSerializer',
    'UserListSerializer',
    'UserDetailSerializer',
    'SubscriptionSerializer',
    'StargazerSerializer',
    'CategorySerializer',
    'CloudPlatformSerializer',
    'CloudPlatformSearchSerializer',
    'TagSerializer',
    'TagSearchSerializer',
    'PlatformSerializer',
    'PlatformSearchSerializer',
    'RepositoryVersionSerializer',
    'TopContributorsSerializer',
    'ImportTaskSerializer',
    'ImportTaskLatestSerializer',
    'RoleTopSerializer',
]


logger = logging.getLogger(__name__)

User = get_user_model()

BASE_FIELDS = ('id', 'url', 'related', 'summary_fields',
               'created', 'modified', 'name')

# Fields that should be summarized regardless of object type.
DEFAULT_SUMMARY_FIELDS = ('name', 'description',)

SUMMARIZABLE_FK_FIELDS = {
    'owner': ('id', 'url', 'username', 'full_name', 'avatar_url'),
    'role': ('id', 'url', 'name',),
}


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
        self.Meta.fields += ('url', 'related', 'summary_fields',
                             'created', 'modified', 'active')

    def get_fields(self):
        # opts = get_concrete_model(self.Meta.model)._meta
        opts = self.Meta.model._meta.concrete_model._meta
        ret = super(BaseSerializer, self).get_fields()
        for key, field in ret.items():
            if key == 'id' and not getattr(field, 'help_text', None):
                field.help_text = u'Database ID for this {}.'.format(
                    opts.verbose_name)
            elif key == 'url':
                field.help_text = u'URL for this {}.'.format(opts.verbose_name)
                field.type_label = 'string'
            elif key == 'related':
                field.help_text = (
                    'Data structure with URLs of related resources.')
                field.type_label = 'object'
            elif key == 'summary_fields':
                field.help_text = (
                    'Data structure with name/description '
                    'for related resources.')
                field.type_label = 'object'
            elif key == 'created':
                field.help_text = (
                    u'Timestamp when this {} was created.'.format(
                        opts.verbose_name))
                field.type_label = 'datetime'
            elif key == 'modified':
                field.help_text = (
                    u'Timestamp when this {} was last modified.'.format(
                        opts.verbose_name))
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


class MeSerializer(BaseSerializer):
    authenticated = serializers.SerializerMethodField()
    staff = serializers.ReadOnlyField(source='is_staff')

    class Meta:
        model = User
        fields = ('id', 'authenticated', 'staff', 'username',)

    def get_summary_fields(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        d = super(MeSerializer, self).get_summary_fields(obj)
        return d

    def get_authenticated(self, obj):
        return obj.is_authenticated()


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
            'avatar_url',
            'cache_refreshed'
        )

    def get_related(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        res = super(UserListSerializer, self).get_related(obj)
        res.update(dict(
            subscriptions=reverse(
                'api:user_subscription_list', args=(obj.pk,)),
            starred=reverse(
                'api:user_starred_list', args=(obj.pk,)),
            repositories=reverse(
                'api:user_repositories_list', args=(obj.pk,)),
            secrets=reverse(
                'api:user_notification_secret_list', args=(obj.pk,)),
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
            'avatar_url',
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
        instance = super(UserDetailSerializer, self).restore_object(
            attrs, instance)
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
            repositories=reverse(
                'api:user_repositories_list', args=(obj.pk,)),
            subscriptions=reverse(
                'api:user_subscription_list', args=(obj.pk,)),
            starred=reverse(
                'api:user_starred_list', args=(obj.pk,)),
            secrets=reverse(
                'api:user_notification_secret_list', args=(obj.pk,)),
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
        fields = BASE_FIELDS + ('description',)


class TagSearchSerializer(TagSerializer):
    roles_count = serializers.IntegerField(read_only=True)

    class Meta(TagSerializer.Meta):
        fields = TagSerializer.Meta.fields + ('roles_count', )


class PlatformSearchSerializer(PlatformSerializer):
    roles_count = serializers.IntegerField(read_only=True)

    class Meta(PlatformSerializer.Meta):
        fields = PlatformSerializer.Meta.fields + ('roles_count',)


class CloudPlatformSearchSerializer(CloudPlatformSerializer):
    roles_count = serializers.IntegerField(read_only=True)

    class Meta(CloudPlatformSerializer.Meta):
        fields = CloudPlatformSerializer.Meta.fields + ('roles_count', )


class RepositoryVersionSerializer(BaseSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = RepositoryVersion
        fields = ('id', 'version', 'tag', 'commit_date',
                  'commit_sha', 'download_url')

    def get_download_url(self, obj):
        return obj.repository.get_download_url(obj.tag)


class TopContributorsSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):
        return {
            'namespace': obj['namespace'],
            'role_count': obj['count']
        }


class ImportTaskSerializer(BaseSerializer):

    class Meta:
        model = ImportTask
        fields = (
            'id',
            'owner',
            'celery_task_id',
            'state',
            'started',
            'finished',
            'modified',
            'created',
            'active',
            'import_branch',
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
        if isinstance(obj, ImportTask):
            return reverse('api:import_task_detail', args=(obj.pk,))
        return obj.get_absolute_url()

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(ImportTaskSerializer, self).get_related(obj)
        res.update({
            'provider': reverse(
                'api:active_provider_detail',
                kwargs={'pk': obj.repository.provider_namespace.provider.pk}),
            'repository': reverse(
                'api:repository_detail', args=(obj.repository.pk,)),
            'notifications': reverse(
                'api:import_task_notification_list', args=(obj.pk,)),
        })
        if obj.repository.provider_namespace.namespace:
            pk = obj.repository.provider_namespace.namespace.pk
            res.update({
                'namespace': reverse('api:namespace_detail', kwargs={'pk': pk})
            })
        return res

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        summary = super(ImportTaskSerializer, self).get_summary_fields(obj)
        summary['notifications'] = [OrderedDict([
            ('id', n.id),
            ('travis_build_url', n.travis_build_url),
            ('commit_message', n.commit_message),
            ('committed_at', n.committed_at),
            ('commit', n.commit)
        ]) for n in obj.notifications.all().order_by('id')]

        summary['task_messages'] = [OrderedDict([
            ('id', g.id),
            ('message_type', g.message_type),
            ('message_text', g.message_text)
        ]) for g in obj.messages.all().order_by('id')]

        summary['namespace'] = {}
        if obj.repository.provider_namespace.namespace:
            summary['namespace'] = {
                'id': obj.repository.provider_namespace.namespace.id,
                'name': obj.repository.provider_namespace.namespace.name
            }
        summary['provider_namespace'] = {
            'id': obj.repository.provider_namespace.id,
            'name': obj.repository.provider_namespace.name
        }
        summary['repository'] = {
            'id': obj.repository.id,
            'name': obj.repository.name,
            'import_branch': obj.repository.import_branch,
            'original_name': obj.repository.original_name
        }
        return summary


class ImportTaskLatestSerializer(BaseSerializer):
    id = serializers.SerializerMethodField()
    namespace = serializers.SerializerMethodField()
    repository_name = serializers.SerializerMethodField()
    repository_id = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = ImportTask
        fields = (
            'id',
            'namespace',
            'repository_name',
            'repository_id',
            'state'
        )

    def get_related(self, obj):
        res = super(ImportTaskLatestSerializer, self).get_related(obj)
        res.update({'repository': reverse(
            'api:repository_detail', args=(obj['repository__id'],))})
        return res

    def get_task_obj(self, task_id):
        try:
            return ImportTask.objects.get(pk=task_id)
        except ObjectDoesNotExist:
            return None

    def get_url(self, obj):
        return reverse('api:import_task_detail', args=(obj['last_id'],))

    def get_id(self, obj):
        return obj['last_id']

    def get_namespace(self, obj):
        return obj['repository__provider_namespace__namespace__name']

    def get_repository_name(self, obj):
        return obj['repository__name']

    def get_repository_id(self, obj):
        return obj['repository__id']

    def get_active(self, obj):
        task = self.get_task_obj(obj['last_id'])
        return task.active if task else None

    def get_created(self, obj):
        task = self.get_task_obj(obj['last_id'])
        return task.created if task else None

    def get_modified(self, obj):
        task = self.get_task_obj(obj['last_id'])
        return task.modified if task else None

    def get_state(self, obj):
        task = self.get_task_obj(obj['last_id'])
        return task.state if task else None


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
        ))
        return res

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Content):
            return reverse('api:role_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()
