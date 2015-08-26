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

try:
    from urllib.parse import urljoin, urlencode
except ImportError:
    from urlparse import urljoin
    from urllib import urlencode

from rest_framework import fields
from rest_framework import serializers
from rest_framework.compat import get_concrete_model

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
    url            = serializers.SerializerMethodField('get_url')
    related        = serializers.SerializerMethodField('get_related')
    summary_fields = serializers.SerializerMethodField('get_summary_fields')

    # make certain fields read only
    created       = serializers.SerializerMethodField('get_created')
    modified      = serializers.SerializerMethodField('get_modified')
    active        = serializers.SerializerMethodField('get_active')

    def get_fields(self):
        opts = get_concrete_model(self.opts.model)._meta
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
            return obj.get_absolute_url()

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
            return obj.created

    def get_modified(self, obj):
        if obj is None:
            return None
        elif isinstance(obj, User):
            return obj.last_login # Not actually exposed for User.
        else:
            return obj.modified

    def get_active(self, obj):
        if obj is None:
            return False
        elif isinstance(obj, User):
            return obj.is_active
        else:
            return obj.active

    def validate_description(self, attrs, source):
        # Description should always be empty string, never null.
        attrs[source] = attrs.get(source, None) or ''
        return attrs

class MeSerializer(BaseSerializer):
    authenticated = serializers.Field(source='is_authenticated')
    staff = serializers.Field(source='is_staff')
    class Meta:
        model = User
        fields = ('id','authenticated','staff','username','summary_fields')

    def get_summary_fields(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        d = super(MeSerializer, self).get_summary_fields(obj)
        d['roles'] = [
            OrderedDict([
             ('id',g.id),
             ('name',g.name),
             ('original_name',g.original_name),
             ('active',g.active),
             ('is_valid',g.is_valid),
             ('description',g.description),
             ('github_user',g.github_user),
             ('github_repo',g.github_repo),
             ('categories',g.categories.all()),
             ('platforms',g.platforms.all()),
             ('dependencies',g.dependencies.all()),
             ('versions', [version.name for version in g.versions.all()]),
             ('min_ansible_version',g.min_ansible_version),
             ('license',g.license),
             ('company',g.company),
             ('average_score',"%0.1f" % round(g.average_score,1)),
             ('import',g.get_last_import()),
            ]) for g in obj.roles.filter().order_by('pk')
        ]
        return d

class VoteSerializer(BaseSerializer):
    """
    A limited serialization of the user model for use
    with the up/down vote lists on ratings
    """
    class Meta:
        model = User
        fields = ('id','url','username')

class UserRoleContributorsSerializer(BaseSerializer):
    avatar_url     = serializers.SerializerMethodField('get_avatar_url')
    avg_role_score = serializers.SerializerMethodField('get_avg_role_score')
    email          = serializers.SerializerMethodField('get_email')
    num_roles      = serializers.SerializerMethodField('get_num_roles')
    staff          = serializers.Field(source='is_staff')

    class Meta:
        model = User
        fields = ('id','url','related','username','email','staff',
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
    avatar_url     = serializers.SerializerMethodField('get_avatar_url')
    avg_rating     = serializers.SerializerMethodField('get_avg_rating')
    num_ratings    = serializers.SerializerMethodField('get_num_ratings')
    email          = serializers.SerializerMethodField('get_email')
    staff          = serializers.Field(source='is_staff')

    class Meta:
        model = User
        fields = ('id','url','related','username','email','staff',
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
    avatar_url     = serializers.SerializerMethodField('get_avatar_url')
    avg_rating     = serializers.SerializerMethodField('get_rating_average')
    avg_role_score = serializers.SerializerMethodField('get_role_average')
    num_ratings    = serializers.SerializerMethodField('get_num_ratings')
    num_roles      = serializers.SerializerMethodField('get_num_roles')
    staff          = serializers.Field(source='is_staff')
    email          = serializers.SerializerMethodField('get_email')

    class Meta:
        model = User
        fields = ('id','url','related','summary_fields','username','password','email','karma','staff',
                 'full_name','date_joined','avatar_url','avg_rating','avg_role_score',
                 'num_ratings','num_roles')

    def get_related(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        res = super(UserListSerializer, self).get_related(obj)
        res.update(dict(
            roles   = reverse('api:user_roles_list', args=(obj.pk,)),
            ratings = reverse('api:user_ratings_list', args=(obj.pk,)),
        ))
        return res

    def get_summary_fields(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        d = super(UserListSerializer, self).get_summary_fields(obj)
        d['roles'] = [
              OrderedDict([
                  ('id', g.id),
                  ('name', g.name),
                  ('num_ratings', g.num_ratings),
                  ('average_score', g.average_score),
              ]) for g in obj.user_roles
        ]
        d['ratings'] = [
            OrderedDict([
                ('id', g.id),
                ('score', round(g.score,1)),
                ('comment', g.comment),
                ('created', g.created),
                ('modified', g.modified),
                ('role_id', g.role.id),
                ('role_name', g.role.name),
                ('role_owner_id', g.role.owner.id),
                ('role_owner_username', g.role.owner.username),
            ]) for g in obj.user_ratings
        ]
        return d

    def get_avatar_url(self, obj):
        return get_user_avatar_url(obj)

    def get_num_ratings(self, obj):
        return len(obj.user_ratings)

    def get_rating_average(self, obj):
        return round(sum([rating.score for rating in obj.user_ratings]) / len(obj.user_ratings), 1) if len(obj.user_ratings) > 0 else 0
    
    def get_num_roles(self, obj):
        return len(obj.user_roles)

    def get_role_average(self, obj):
        cnt = 0
        total_score = 0
        for role in obj.user_roles:
            if role.average_score > 0:
                cnt += 1
                total_score += role.average_score
        return round(total_score / cnt,1) if cnt > 0 else 0

    def get_email(self, obj):
        if self.context['request'].user.is_staff:
            return obj.email
        else:
            return ''

class UserDetailSerializer(BaseSerializer):
    password = serializers.WritableField(
        required=False, default='', help_text='Write-only field used to change the password.'
    )
    avatar_url     = serializers.SerializerMethodField('get_avatar_url')
    avg_rating     = serializers.SerializerMethodField('get_rating_average')
    avg_role_score = serializers.SerializerMethodField('get_role_average')
    num_ratings    = serializers.SerializerMethodField('get_num_ratings')
    num_roles      = serializers.SerializerMethodField('get_num_roles')
    staff          = serializers.Field(source='is_staff')
    email          = serializers.SerializerMethodField('get_email')

    class Meta:
        model = User
        fields = ('id','url','related','summary_fields','username','password','email','karma','staff',
                 'full_name','date_joined','avatar_url','avg_rating','avg_role_score','num_ratings','num_roles')

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
            roles   = reverse('api:user_roles_list', args=(obj.pk,)),
            ratings = reverse('api:user_ratings_list', args=(obj.pk,)),
        ))
        return res

    def get_summary_fields(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        d = super(UserDetailSerializer, self).get_summary_fields(obj)
        d['roles'] = [
            OrderedDict([
                ('id', g.id),
                ('name', g.name),
                ('average_score', round(g.average_score, 1)),
            ]) for g in obj.roles.filter(active=True, is_valid=True).order_by('pk')
        ]
        d['ratings'] = [
            OrderedDict([
                ('id', g.id),
                ('score', "%0.1f" % g.score),
                ('comment', g.comment),
                ('created', g.created),
                ('modified', g.modified),
                ('role_id', g.role.id),
                ('role_name', g.role.name),
                ('role_owner_id', g.role.owner.id),
                ('role_owner_username', g.role.owner.username),
            ]) for g in obj.ratings.filter(active=True, role__active=True, role__is_valid=True).order_by('-created')
        ]
        return d

    def get_avatar_url(self, obj):
        return get_user_avatar_url(obj)

    def get_num_ratings(self, obj):
        return round(obj.get_num_ratings(),1)

    def get_rating_average(self, obj):
        return round(obj.get_rating_average(),1)

    def get_num_roles(self, obj):
        return obj.get_num_roles()

    def get_role_average(self, obj):
        return round(obj.get_role_average(),1)

    def get_email(self, obj):
        if self.context['request'].user.is_staff:
            return obj.email
        else:
            return ''

class PlatformSerializer(BaseSerializer):
    class Meta:
        model = Platform
        fields = BASE_FIELDS + ('release',)

class CategorySerializer(BaseSerializer):
    num_roles = serializers.SerializerMethodField('get_num_roles')
    class Meta:
        model = Category
        fields = BASE_FIELDS + ('num_roles',)

    def get_num_roles(self, obj):
        return obj.get_num_roles()

class RoleVersionSerializer(BaseSerializer):
    class Meta:
        model = RoleVersion
        fields = ('id','name','release_date',)

class RoleImportSerializer(BaseSerializer):
    class Meta:
        model = RoleImport
        fields = ('celery_task_id','released',)

class RoleRatingSerializer(BaseSerializer):
    
    class Meta:
        model = RoleRating
        fields = (
            'id','url','role','related','summary_fields','comment','created','modified','score'
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
        res.update(dict(
            up_votes = reverse('api:rating_up_votes_list', args=(obj.pk,)),
            down_votes = reverse('api:rating_down_votes_list', args=(obj.pk,)),
        ))
        return res

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(RoleRatingSerializer, self).get_summary_fields(obj)
        d['role'] = {
            'id': obj.role.id,
            'name': obj.role.name,
            'owner_id': obj.role.owner.id,
            'owner_username': obj.role.owner.username
        }
        d['owner'] = {
            'id': obj.owner.id,
            'username': obj.owner.username,
            'full_name': obj.owner.full_name,
            'avatar_url': get_user_avatar_url(obj.owner),
        }

        return d

class RoleListSerializer(BaseSerializer):
    average_score        = serializers.SerializerMethodField('get_average_score')
    readme_html          = serializers.SerializerMethodField('get_readme_html')

    class Meta:
        model = Role
        fields = BASE_FIELDS + ('average_score','bayesian_score','num_ratings',
                                'github_user','github_repo','min_ansible_version','issue_tracker_url',
                                'license','company','description','readme_html')

    def to_native(self, obj):
        ret = super(RoleListSerializer, self).to_native(obj)
        return ret

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(RoleListSerializer, self).get_related(obj)
        res.update(dict(
            owner    = reverse('api:user_detail', args=(obj.owner.pk,)),
	        authors  = reverse('api:role_authors_list', args=(obj.pk,)),
            dependencies = reverse('api:role_dependencies_list', args=(obj.pk,)),
            imports  = reverse('api:role_imports_list', args=(obj.pk,)),
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

        d['categories'] = [g.name for g in obj.categories.all()]
        d['dependencies'] = [str(g) for g in obj.dependencies.all()]
        d['platforms'] = [{'name':g.name,'release':g.release} for g in obj.platforms.all()]
        d['versions'] = [{'name':g.name,'release_date':g.release_date} for g in obj.versions.all()]
        d['owner'] = {
            'id': obj.owner.id,
            'username': obj.owner.username,
            'full_name': obj.owner.full_name,
            'staff': obj.owner.is_staff,
            'avatar_url': get_user_avatar_url(obj.owner),
        }

        return d

    def get_average_score(self, obj):
        return round(obj.average_score, 1)

    def get_readme_html(self, obj):
        if obj is None:
            return ''
        return markdown.markdown(html_decode(obj.readme), extensions=['extra'])

class RoleTopSerializer(BaseSerializer):
    # num_ratings = serializers.Field(source='num_ratings')
    average_score = serializers.SerializerMethodField('get_average_score')

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
            owner    = reverse('api:user_detail', args=(obj.owner.pk,)),
	        authors  = reverse('api:role_authors_list', args=(obj.pk,)),
            dependencies = reverse('api:role_dependencies_list', args=(obj.pk,)),
            imports  = reverse('api:role_imports_list', args=(obj.pk,)),
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
    #num_ratings          = serializers.SerializerMethodField('get_num_ratings')
    average_score        = serializers.SerializerMethodField('get_average_score')
    #average_composite    = serializers.SerializerMethodField('get_average_composite')
    #num_aw_ratings       = serializers.SerializerMethodField('get_num_aw_ratings')
    #average_aw_score     = serializers.SerializerMethodField('get_average_aw_score')
    #average_aw_composite = serializers.SerializerMethodField('get_average_aw_composite')
    readme_html          = serializers.SerializerMethodField('get_readme_html')

    class Meta:
        model = Role
        fields = BASE_FIELDS + ('average_score','bayesian_score','num_ratings',
                                'github_user','github_repo','min_ansible_version','issue_tracker_url',
                                'license','company','description','readme_html')

    def to_native(self, obj):
        ret = super(RoleDetailSerializer, self).to_native(obj)
        return ret

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(RoleDetailSerializer, self).get_related(obj)
        res.update(dict(
            owner    = reverse('api:user_detail', args=(obj.owner.pk,)),
	    authors  = reverse('api:role_authors_list', args=(obj.pk,)),
            dependencies = reverse('api:role_dependencies_list', args=(obj.pk,)),
            imports  = reverse('api:role_imports_list', args=(obj.pk,)),
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
        d = super(RoleDetailSerializer, self).get_summary_fields(obj)

        d['categories'] = [g.name for g in obj.categories.all()]
        d['dependencies'] = [str(g) for g in obj.dependencies.all()]
        d['ratings'] = [{'id':g.id, 'score':g.score} for g in obj.ratings.filter(owner__is_active=True)]
        d['platforms'] = [{'name':g.name,'release':g.release} for g in obj.platforms.all()]
        d['versions'] = [{'name':g.name,'release_date':g.release_date} for g in obj.versions.all()]
        d['owner'] = {
            'id': obj.owner.id,
            'username': obj.owner.username,
            'full_name': obj.owner.full_name,
            'staff': obj.owner.is_staff,
            'avatar_url': get_user_avatar_url(obj.owner),
        }

        return d

    #def get_num_ratings(self, obj):
    #    return obj.get_num_ratings()

    def get_average_score(self, obj):
        return "%0.1f" % obj.average_score

    # def get_average_composite(self, obj):
    #     composite = obj.get_average_composite()
    #     for k in composite:
    #         composite[k] = "%0.1f" % composite[k]
    #     return composite

    # def get_num_aw_ratings(self, obj):
    #     return obj.get_num_aw_ratings()

    # def get_average_aw_score(self, obj):
    #     return "%0.1f" % obj.get_average_aw_score()

    # def get_average_aw_composite(self, obj):
    #     composite = obj.get_average_aw_composite()
    #     for k in composite:
    #         composite[k] = "%0.1f" % composite[k]
    #     return composite

    def get_readme_html(self, obj):
        if obj is None:
            return ''
        return markdown.markdown(html_decode(obj.readme), extensions=['extra'])
