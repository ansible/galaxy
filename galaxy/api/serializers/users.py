import logging

from collections import OrderedDict

from allauth.account.models import EmailAddress

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse

from rest_framework import serializers

from .serializers import BaseSerializer

logger = logging.getLogger(__name__)

User = get_user_model()

USER_FIELDS = (
    'id', 'url', 'related', 'summary_fields', 'created', 'modified',
    'username', 'staff', 'full_name', 'date_joined', 'avatar_url',
    'notify_survey', 'notify_import_fail', 'notify_import_success',
    'notify_content_release', 'notify_author_release',
    'notify_galaxy_announce',
)

__all__ = [
    'ActiveUserSerializer',
    'UserListSerializer',
    'UserDetailSerializer'
]


class ActiveUserSerializer(BaseSerializer):
    authenticated = serializers.SerializerMethodField()
    staff = serializers.ReadOnlyField(source='is_staff')
    primary_email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = USER_FIELDS + ('authenticated', 'primary_email')

    def get_summary_fields(self, obj):
        if not obj or not obj.is_authenticated():
            return {}
        d = super(ActiveUserSerializer, self).get_summary_fields(obj)
        return d

    def get_authenticated(self, obj):
        return obj.is_authenticated()

    def get_primary_email(self, obj):
        if obj and not isinstance(obj, AnonymousUser):
            emails = EmailAddress.objects.filter(user=obj, primary=True)
            if emails:
                return emails[0].email
        return None


class UserListSerializer(BaseSerializer):
    staff = serializers.ReadOnlyField(source='is_staff')

    class Meta:
        model = User
        fields = USER_FIELDS

    def get_related(self, obj):
        if not obj or not obj.is_authenticated():
            return {}
        res = super(UserListSerializer, self).get_related(obj)
        res.update(dict(
            subscriptions=reverse(
                'api:user_subscription_list', args=(obj.pk,)),
            starred=reverse(
                'api:user_starred_list', args=(obj.pk,)),
            repositories=reverse(
                'api:user_repositories_list', args=(obj.pk,)),
            email=reverse(
                'api:user_email_list', args=(obj.pk,)),
        ))
        return res

    def get_summary_fields(self, obj):
        if not obj or not obj.is_authenticated():
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


class UserDetailSerializer(UserListSerializer):
    id = serializers.IntegerField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    avatar_url = serializers.URLField(read_only=True)
    username = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    notify_survey = serializers.BooleanField(default=False)
    notify_import_fail = serializers.BooleanField(default=False)
    notify_import_success = serializers.BooleanField(default=False)
    notify_content_release = serializers.BooleanField(default=False)
    notify_author_release = serializers.BooleanField(default=False)
    notify_galaxy_announce = serializers.BooleanField(default=False)
