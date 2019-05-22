from collections import OrderedDict

from django.urls import reverse
from rest_framework import serializers

from galaxy.main.models import NotificationSecret, Notification

from .serializers import BaseSerializer

__all__ = [
    'NotificationSecretSerializer',
    'NotificationSerializer',

]


class NotificationSecretSerializer(BaseSerializer):
    secret = serializers.SerializerMethodField()

    class Meta:
        model = NotificationSecret
        fields = (
            'id',
            'url',
            'related',
            'summary_fields',
            'created',
            'modified',
            'owner',
            'github_user',
            'github_repo',
            'source',
            'secret',
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
        return '******'


class NotificationSerializer(BaseSerializer):
    class Meta:
        model = Notification
        fields = (
            'id',
            'url',
            'related',
            'summary_fields',
            'created',
            'modified',
            'owner',
            'source',
            'github_branch',
            'travis_build_url',
            'travis_status',
            'commit_message',
            'committed_at',
            'commit'
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
        d = super().get_summary_fields(obj)
        d['owner'] = OrderedDict([
            ('id', obj.owner.id),
            ('username', obj.owner.username)
        ])
        return d

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super().get_related(obj)
        res.update(dict(
            owner=reverse('api:user_detail', args=(obj.owner.id,)),
        ))
        return res
