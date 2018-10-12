from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .serializers import BaseSerializer

__all__ = [
    'TokenSerializer',
]

User = get_user_model()


class TokenSerializer(BaseSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = ('url', 'related', 'summary_fields', 'token',
                  'created')

    def get_url(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return ''
        return reverse('api:user_token_view', args=(obj.user.pk,))

    def get_related(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        res = super(TokenSerializer, self).get_related(obj)
        res.update({
            'user': reverse(
                'api:user_detail', kwargs={'pk': obj.user.pk})
        })
        return res

    def get_summary_fields(self, obj):
        if obj is None or isinstance(obj, AnonymousUser):
            return {}
        res = super(TokenSerializer, self).get_summary_fields(obj)
        res['user'] = {
            'id': obj.user.id,
            'username': obj.user.username,
        }
        return res

    def get_token(self, obj):
        return obj.key
