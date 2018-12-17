
import logging

from allauth.account.models import EmailAddress, EmailConfirmation
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from galaxy.api.views import base_views
from galaxy.api import serializers
from galaxy.worker.tasks import user_notifications

from rest_framework.response import Response

__all__ = [
    'UserEmailList',
    'EmailList',
    'EmailDetail',
    'EmailVerification',
    'EmailVerificationDetail'
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


class EmailVerification(base_views.ListCreateAPIView):
    serializer_class = serializers.EmailVerificationSerializer
    model = EmailConfirmation

    # We don't want to divulge any information about the confirmation keys in
    # the database since they are secret.
    def get(self, request, *args, **kwargs):
        return Response("")

    def get_queryset(self):
        return self.model.objects.none()

    # Creates key
    def post(self, request, *args, **kwargs):
        email = get_object_or_404(
            EmailAddress,
            pk=request.data['email_address']
        )

        if (email.verified):
            return Response({
                'email_address': email.pk,
                'verified': True
            })

        verification = self.model.create(email)
        user_notifications.email_verification(
            email=email.email,
            code=verification.key,
            username=request.user.username
        )

        serializer = self.get_serializer(instance=verification)
        return Response(serializer.data)


class EmailVerificationDetail(base_views.RetrieveAPIView):
    serializer_class = serializers.EmailVerificationSerializer
    model = EmailConfirmation
    lookup_field = 'key'

    def get(self, request, *args, **kwargs):
        key = self.get_object()

        key.email_address.verified = True
        key.email_address.save()

        return Response(self.get_serializer(instance=key).data)
