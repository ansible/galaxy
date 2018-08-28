from collections import OrderedDict

from allauth.account.models import EmailAddress
from django.core.urlresolvers import reverse
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from rest_framework import serializers
from .serializers import BaseSerializer

__all__ = [
    'EmailSerializer',
]


class IsVerified(object):

    def __call__(self, value):
        if self.instance and self.instance.verified:
            # This is an Update to a verified address
            if self.instance.email != self.data.get('email'):
                message = 'Verified email addresses cannot be modified'
                raise serializers.ValidationError(message)

    def set_context(self, serializer_field):
        self.instance = getattr(serializer_field.parent, 'instance', None)
        self.data = getattr(serializer_field.parent, 'initial_data', None)


class EmailSerializer(BaseSerializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=EmailAddress.objects.all()),
            IsVerified()
        ]
    )
    verified = serializers.BooleanField(read_only=True)
    primary = serializers.BooleanField(default=False)

    class Meta:
        model = EmailAddress
        fields = (
            'url',
            'related',
            'summary_fields',
            'id',
            'email',
            'verified',
            'primary'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=EmailAddress.objects.all(),
                fields=('email', 'user', 'primary'),
                message="Only one email address can be primary"),
        ]

    def get_url(self, obj):
        if obj is None:
            return ''
        return reverse('api:email_detail', args=(obj.pk,))

    def get_related(self, obj):
        d = super(EmailSerializer, self).get_related(obj)
        d['user'] = reverse('api:user_detail', args=(obj.user.pk,))
        return d

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(EmailSerializer, self).get_summary_fields(obj)
        d['user'] = OrderedDict([
            ('id', obj.user.id),
            ('username', obj.user.username)
        ])
        return d
