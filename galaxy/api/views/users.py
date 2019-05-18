import logging

from rest_framework import exceptions

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

from galaxy.api import serializers
from galaxy.api.views import base_views
from galaxy.main import models


__all__ = [
    'UserList',
    'UserDetail',
    'ActiveUserView',
    'UserNotificationSecretList',
    'UserRepositoriesList',
    'UserRolesList',
    'UserStarredList',
    'UserSubscriptionList',
]

logger = logging.getLogger(__name__)

User = get_user_model()


class UserDetail(base_views.RetrieveUpdateAPIView):
    model = User
    serializer_class = serializers.UserSerializer

    def get_object(self, qs=None):
        obj = super().get_object()
        if not obj.is_active:
            raise exceptions.PermissionDenied()
        return obj


class UserList(base_views.ListAPIView):
    model = User
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True)


class ActiveUserView(base_views.RetrieveAPIView):
    model = User
    serializer_class = serializers.ActiveUserSerializer
    view_name = 'Me'

    def get_object(self):
        try:
            obj = self.model.objects.get(pk=self.request.user.pk)
        except ObjectDoesNotExist:
            obj = AnonymousUser()
        return obj


class UserRepositoriesList(base_views.SubListAPIView):
    model = models.Repository
    serializer_class = serializers.RepositorySerializer
    parent_model = User
    relationship = 'repositories'


class UserRolesList(base_views.SubListAPIView):
    model = models.Content
    serializer_class = serializers.RoleDetailSerializer
    parent_model = User
    relationship = 'roles'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(active=True, is_valid=True)


class UserSubscriptionList(base_views.SubListAPIView):
    model = models.Subscription
    serializer_class = serializers.SubscriptionSerializer
    parent_model = User
    relationship = 'subscriptions'


class UserStarredList(base_views.SubListAPIView):
    model = models.Stargazer
    serializer_class = serializers.StargazerSerializer
    parent_model = User
    relationship = 'starred'


class UserNotificationSecretList(base_views.SubListAPIView):
    model = models.NotificationSecret
    serializer_class = serializers.NotificationSecretSerializer
    parent_model = User
    relationship = 'notification_secrets'
