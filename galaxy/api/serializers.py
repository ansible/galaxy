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

import hashlib
import markdown
import collections

try:
    from urllib.parse import urljoin, urlencode
except ImportError:
    from urlparse import urljoin
    from urllib import urlencode

from rest_framework import fields
from rest_framework import serializers
#from rest_framework.compat import get_concrete_model

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Avg
from django.utils import text, html
from collections import OrderedDict

from avatar.conf import settings
from avatar.util import get_primary_avatar, get_default_avatar_url, force_bytes
from avatar.models import Avatar

# haystack
from drf_haystack.serializers import HaystackSerializer

# galaxy
from galaxy.main.search_indexes import RoleIndex
from galaxy.api.aggregators import *
from galaxy.api.utils import html_decode
from galaxy.main.models import *

User = get_user_model()

BASE_FIELDS = ('id', 'url', 'related', 'summary_fields', 'created', 'modified', 'name')

# Fields that should be summarized regardless of object type.
DEFAULT_SUMMARY_FIELDS = ('name', 'description',)

SUMMARIZABLE_FK_FIELDS = {
    'owner' : ('id','url','username', 'full_name', 'avatar_url'),
    'role'  : ('id','url','name',),
}

def get_user_avatar_url(obj):
    size=96
    params = {'s': str(size)}
    if settings.AVATAR_GRAVATAR_DEFAULT:
        params['d'] = settings.AVATAR_GRAVATAR_DEFAULT
    path = "%s/?%s" % (
        hashlib.md5(force_bytes(obj.email)).hexdigest(),
        urlencode(params),
    )
    return urljoin('//www.gravatar.com/avatar/', path) #

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

    #def to_representation(self, obj):
    #    super(BaseSerializer, self).to_representation(obj)

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

class UserRoleContributorsSerializer(BaseSerializer):
    avatar_url     = serializers.SerializerMethodField()
    avg_role_score = serializers.SerializerMethodField()
    email          = serializers.SerializerMethodField()
    num_roles      = serializers.SerializerMethodField()
    staff          = serializers.ReadOnlyField(source='is_staff')

    class Meta:
        model = User
        fields = ('id','username','email','staff',
                 'full_name','date_joined','avatar_url','avg_role_score',
                 'num_roles')

    def get_related(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        res = super(UserRoleContributorsSerializer, self).get_related(obj)
        res.update(dict(
            roles   = reverse('api:user_roles_list', args=(obj.pk,)),
            ratings = reverse('api:user_ratings_list', args=(obj.pk,)),
        ))
        return res

    def get_avatar_url(self, obj):
        return get_user_avatar_url(obj)

    def get_email(self, obj):
        if self.context['request'].user.is_staff:
            return obj.email
        else:
            return ''

    def get_num_roles(self, obj):
        return obj.num_roles
    
    def get_avg_role_score(self, obj):
        cnt = 0
        total = 0
        for role in obj.scored_roles:
            if role.average_score > 0:
                cnt += 1
                total += role.average_score
        return round(total / cnt,1) if cnt > 0 else 0

class UserRatingContributorsSerializer(BaseSerializer):
    avatar_url     = serializers.SerializerMethodField()
    avg_rating     = serializers.SerializerMethodField()
    num_ratings    = serializers.SerializerMethodField()
    email          = serializers.SerializerMethodField()
    staff          = serializers.ReadOnlyField(source='is_staff')

    class Meta:
        model = User
        fields = ('id','url','username','email','staff',
                 'full_name','date_joined','avatar_url','avg_rating',
                 'num_ratings')

    def get_related(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        res = super(UserRatingContributorsSerializer, self).get_related(obj)
        res.update(dict(
            roles   = reverse('api:user_roles_list', args=(obj.pk,)),
            ratings = reverse('api:user_ratings_list', args=(obj.pk,)),
        ))
        return res

    def get_avatar_url(self, obj):
        return get_user_avatar_url(obj)

    def get_email(self, obj):
        if self.context['request'].user.is_staff:
            return obj.email
        else:
            return ''

    def get_num_ratings(self, obj):
        return obj.num_ratings
    
    def get_avg_rating(self, obj):
        return round(obj.avg_rating,1)
    
class UserListSerializer(BaseSerializer):
    avatar_url     = serializers.SerializerMethodField()
    avg_rating     = serializers.SerializerMethodField()
    # avg_role_score = serializers.SerializerMethodField()
    num_ratings    = serializers.SerializerMethodField()
    # num_roles      = serializers.SerializerMethodField()
    staff          = serializers.ReadOnlyField(source='is_staff')
    email          = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id','username','email','karma','staff',
                 'full_name','date_joined','avatar_url','avg_rating',
                 #'avg_role_score',
                 'num_ratings',
                 #'num_roles'
                 )

    def get_related(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        res = super(UserListSerializer, self).get_related(obj)
        res.update(dict(
            ratings = reverse('api:user_ratings_list', args=(obj.pk,)),
            repositories = reverse('api:user_repositories_list', args=(obj.pk,))
        ))
        return res

    def get_summary_fields(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        d = super(UserListSerializer, self).get_summary_fields(obj)
        d['ratings'] = [
            OrderedDict([
                ('id', g.id),
                ('score', round(g.score,1)),
                ('comment', g.comment),
                ('created', g.created),
                ('modified', g.modified),
                ('role_id', g.role.id),
                ('role_namespace', g.role.namespace),
                ('role_name', g.role.name),
           ]) for g in obj.user_ratings
        ]
        return d

    def get_avatar_url(self, obj):
        return get_user_avatar_url(obj)

    def get_num_ratings(self, obj):
        return len(obj.user_ratings)

    def get_avg_rating(self, obj):
        return round(sum([rating.score for rating in obj.user_ratings]) / len(obj.user_ratings), 1) if len(obj.user_ratings) > 0 else 0
    
    # def get_num_roles(self, obj):
    #     return len(obj.user_roles)

    # def get_avg_role_score(self, obj):
    #     cnt = 0
    #     total_score = 0
    #     for role in obj.user_roles:
    #         if role.average_score > 0:
    #             cnt += 1
    #             total_score += role.average_score
    #     return round(total_score / cnt,1) if cnt > 0 else 0

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
    avatar_url     = serializers.SerializerMethodField()
    avg_rating     = serializers.SerializerMethodField()
    # avg_role_score = serializers.SerializerMethodField()
    num_ratings    = serializers.SerializerMethodField()
    staff          = serializers.ReadOnlyField(source='is_staff')
    email          = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id','username','password','email','karma','staff',
                 'full_name','date_joined','avatar_url','avg_rating',
                 #'avg_role_score',
                 'num_ratings',
                 #'num_roles'
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
        instance = super(UserSerializer, self).restore_object(attrs, instance)
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
            ratings = reverse('api:user_ratings_list', args=(obj.pk,)),
            repositories = reverse('api:user_repositories_list', args=(obj.pk,))
        ))
        return res

    def get_summary_fields(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        d = super(UserDetailSerializer, self).get_summary_fields(obj)
        d['ratings'] = [
            OrderedDict([
                ('id', g.id),
                ('score', "%0.1f" % g.score),
                ('comment', g.comment),
                ('created', g.created),
                ('modified', g.modified),
                ('role_id', g.role.id),
                ('role_namespace', g.role.namespace),
                ('role_name', g.role.name),
            ]) for g in obj.ratings.filter(active=True, role__active=True, role__is_valid=True).order_by('-created')
        ]
        return d

    def get_avatar_url(self, obj):
        return get_user_avatar_url(obj)

    def get_num_ratings(self, obj):
        return round(obj.get_num_ratings(),1)

    def get_avg_rating(self, obj):
        return round(obj.get_rating_average(),1)

    def get_num_roles(self, obj):
        return obj.get_num_roles()

    def get_avg_role_score(self, obj):
        return round(obj.get_role_average(),1)

    def get_email(self, obj):
        if self.context['request'].user.is_staff:
            return obj.email
        else:
            return ''

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
            return reverse('api:user_repos_detail', args=(obj.pk,))
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


class NotificationSecretSerializer(BaseSerializer):
    secret     = serializers.SerializerMethodField()

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
        ]) for r in obj.roles.all() ]
        d['imports'] = [OrderedDict([
            ('id', t.id) 
        ]) for t in obj.imports.all() ]
        return d

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(NotificationSerializer, self).get_related(obj)
        res.update(dict(
            roles = reverse('api:notification_roles_list', args=(obj.pk,)),
            imports = reverse('api:notification_imports_list', args=(obj.pk,))
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
            'role',
            'owner',
            'alternate_role_name',
            'celery_task_id',
            'state',
            'started',
            'finished',
            'modified',
            'created',
            'active'
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
            role = reverse('api:role_detail', args=(obj.role_id,))
        ))
        if obj.notifications.count() > 0:
            key = obj.notifications.all()[0].id
            res.update(dict(
                notification = reverse('api:notification_detail', args=(key,))
            ))
        return res 

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(ImportTaskSerializer, self).get_summary_fields(obj)
        d['role'] = OrderedDict([
            ('id',obj.role.id),
            ('namespace',obj.role.namespace),
            ('name',obj.role.name)
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
        d['details'] = OrderedDict([
            ('id', g.id),
            ('state', g.state),
            ('github_user', g.github_user),
            ('github_repo', g.github_repo),
            ('github_reference', g.github_reference),
            ('role', g.role.id),
            ('modified', g.modified),
            ('created', g.created)
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


class RoleRatingSerializer(BaseSerializer):
    
    class Meta:
        model = RoleRating
        fields = (
            'id','url','role','comment','created','modified','score'
        )

    # 'staff_rating'
    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Role):
            return reverse('api:role_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(RoleRatingSerializer, self).get_related(obj)
        return res

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(RoleRatingSerializer, self).get_summary_fields(obj)
        d['role'] = {
            'id': obj.role.id,
            'namespace': obj.role.namespace,
            'name': obj.role.name,
        }
        d['owner'] = {
            'id': obj.owner.id,
            'username': obj.owner.username,
            'full_name': obj.owner.full_name,
            'avatar_url': get_user_avatar_url(obj.owner),
        }

        return d

class RoleListSerializer(BaseSerializer):
    average_score        = serializers.SerializerMethodField()
    readme_html          = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = BASE_FIELDS + ('namespace','average_score','bayesian_score','num_ratings','is_valid',
                                'github_user','github_repo','min_ansible_version','issue_tracker_url',
                                'license','company','description', 'readme_html','travis_status_url',
                                'stargazers_count', 'watchers_count', 'forks_count', 'open_issues_count',
                                'commit', 'commit_message','commit_url')

    def to_native(self, obj):
        ret = super(RoleListSerializer, self).to_native(obj)
        return ret

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(RoleListSerializer, self).get_related(obj)
        res.update(dict(
            dependencies = reverse('api:role_dependencies_list', args=(obj.pk,)),
            imports  = reverse('api:role_import_task_list', args=(obj.pk,)),
            ratings  = reverse('api:role_ratings_list', args=(obj.pk,)),
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

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(RoleListSerializer, self).get_summary_fields(obj)
        d['dependencies'] = [str(g) for g in obj.dependencies.all()]
        d['platforms'] = [{'name':g.name,'release':g.release} for g in obj.platforms.all()]
        d['tags'] = [{'name':g.name} for g in obj.tags.all()]
        d['versions'] = [{'name':g.name,'release_date':g.release_date} for g in obj.versions.all()]
        return d

    def get_average_score(self, obj):
        return round(obj.average_score, 1)

    def get_readme_html(self, obj):
        if obj is None:
            return ''
        return markdown.markdown(html_decode(obj.readme), extensions=['extra'])

class RoleTopSerializer(BaseSerializer):
    # num_ratings = serializers.Field(source='num_ratings')
    average_score = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = BASE_FIELDS + ('average_score','bayesian_score','num_ratings',
                                'github_user','github_repo','min_ansible_version','issue_tracker_url',
                                'license','company','description')

    # 'num_aw_ratings','average_aw_score'
    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(RoleTopSerializer, self).get_related(obj)
        res.update(dict(
            dependencies = reverse('api:role_dependencies_list', args=(obj.pk,)),
            imports  = reverse('api:role_import_task_list', args=(obj.pk,)),
            ratings  = reverse('api:role_ratings_list', args=(obj.pk,)),
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

    def get_average_score(self, obj):
        return round(obj.average_score, 1)

class RoleDetailSerializer(BaseSerializer):
    average_score        = serializers.SerializerMethodField()
    readme_html          = serializers.SerializerMethodField()
    tags                 = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = BASE_FIELDS + ('average_score','bayesian_score','num_ratings','is_valid',
                                'github_user','github_repo','github_branch','min_ansible_version','issue_tracker_url',
                                'license','company','description','readme_html', 'tags','travis_status_url',
                                'stargazers_count', 'watchers_count', 'forks_count', 'open_issues_count',
                                'commit', 'commit_message','commit_url')

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
            ratings  = reverse('api:role_ratings_list', args=(obj.pk,)),
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
        d['dependencies'] = [{ 'id': g.id, 'name': str(g) } for g in obj.dependencies.all()]
        d['ratings'] = [{'id':g.id, 'score':g.score} for g in obj.ratings.filter(owner__is_active=True)]
        d['platforms'] = [{'name':g.name,'release':g.release} for g in obj.platforms.all()]
        d['tags'] = [{'name':g.name} for g in obj.tags.all()]
        d['versions'] = [{'name':g.name,'release_date':g.release_date} for g in obj.versions.all()]
        return d
    
    def get_average_score(self, obj):
        return "%0.1f" % obj.average_score

    def get_readme_html(self, obj):
        if obj is None:
            return ''
        return markdown.markdown(html_decode(obj.readme), extensions=['extra'])

class RoleSearchSerializer(HaystackSerializer):
    id = serializers.SerializerMethodField()
    platforms = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        # The `index_classes` attribute is a list of which search indexes
        # we want to include in the search.
        index_classes = [RoleIndex]

        # The `fields` contains all the fields we want to include.
        # NOTE: Make sure you don't confuse these with model attributes. These
        # fields belong to the search index!
        fields = [
            "username", "name", "description", "github_user", "github_repo", "github_branch",
            "tags", "platforms", "average_score", "num_ratings", "created", "modified", "text",
            "autocomplete", "sort_name", "platforms_autocomplete", "tags_autocomplete",
            "username_autocomplete", "travis_status_url", "stargazers_count", "watchers_count",
            "forks_count", "open_issues_count"
        ]

    def get_average_score(self, instance):
        return round(instance.average_score,1)

    def get_id(self, instance):
        return int(instance.pk)

    def get_platforms(self, instance):
        return [p for p in instance.platforms]

    def get_tags(self, instance):
        return [t for t in instance.tags]

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
