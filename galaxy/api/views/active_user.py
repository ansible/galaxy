import logging

from rest_framework import exceptions

from galaxy.api import serializers
from galaxy.api.views import base_views
from galaxy.main import models


__all__ = [
    'ActiveUserPreferencesView',
    'ActiveUserNotificationsView',
]

logger = logging.getLogger(__name__)


class ActiveUserPreferencesView(base_views.RetrieveUpdateAPIView):
    model = models.UserPreferences
    serializer_class = serializers.ActiveUserPreferencesSerializer
    view_name = 'my_preferences'

    def get_object(self):
        if not self.request.user.is_authenticated():
            raise exceptions.NotAuthenticated()
        obj, created = self.model.objects.get_or_create(
            pk=self.request.user.pk
        )
        return obj


class ActiveUserNotificationsView(base_views.ListAPIView):
    model = models.UserNotification
    serializer_class = serializers.ActiveUserNotificationSerializer
    view_name = 'my_notifications'

    def get_queryset(self):
        obj = self.model.objects.filter(
            user=self.request.user
        )
        return obj
