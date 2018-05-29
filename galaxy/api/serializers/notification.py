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
        except Exception:
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
        return d

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(NotificationSerializer, self).get_related(obj)
        res.update(dict(
            owner=reverse('api:user_detail', args=(obj.owner.id,)),
        ))
        return res
