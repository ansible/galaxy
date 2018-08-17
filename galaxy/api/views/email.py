
import logging

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from galaxy.api.views import base_views
from galaxy.api import serializers

__all__ = [
    'UserEmailList',
    'EmailList',
    'EmailDetail'
]

logger = logging.getLogger(__name__)
User = get_user_model()


class UserEmailList(base_views.SubListAPIView):
    model = EmailAddress
    serializer_class = serializers.EmailSerializer
    parent_model = User
    relationship = 'emailaddress_set'

    def get_queryset(self):
        user_id = self.kwargs.get(self.lookup_field)
        if not self.request.user.is_staff:
            if self.request.user.id != int(user_id):
                # Non-admin access own email addresses only
                raise PermissionDenied()
        return super(UserEmailList, self).get_queryset()


class EmailList(base_views.ListCreateAPIView):
    model = EmailAddress
    serializer_class = serializers.EmailSerializer

    def get_queryset(self):
        qs = super(EmailList, self).get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs


class EmailDetail(base_views.RetrieveUpdateDestroyAPIView):
    model = EmailAddress
    serializer_class = serializers.EmailSerializer

    def get_object(self, qs=None):
        obj = super(EmailDetail, self).get_object()
        if not self.request.user.is_staff:
            if obj.user != self.request.user:
                # Non-admin access own email addresses only
                raise PermissionDenied()
        return obj
