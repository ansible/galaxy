import logging

from rest_framework import exceptions
from rest_framework.response import Response

from galaxy.api import serializers
from galaxy.api.views import base_views
from galaxy.main import models


__all__ = [
    'ActiveUserPreferencesView',
    'ActiveUserNotificationsView',
    'ActiveUserNotificationsDetailView',
    'ActiveUserUnreadNotificationView',
    'ActiveUserClearNotificationView'
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(
            instance=instance,
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        repos = set(serializer.validated_data['repositories_followed']) ^ \
            set(instance.repositories_followed.all())

        authors = set(serializer.validated_data['namespaces_followed']) ^ \
            set(instance.namespaces_followed.all())

        serializer.save()

        for repo in repos:
            count = models.UserPreferences.objects.filter(
                repositories_followed=repo).count()
            name = repo.provider_namespace.namespace.name
            fields = {
                'content_name': '{}.{}'.format(name, repo.name),
                'content_id': repo.id,
                'follower_count': count,
            }

            serializers.influx_insert_internal({
                'measurement': 'content_follower',
                'fields': fields
            })

        for author in authors:
            count = models.UserPreferences.objects.filter(
                namespaces_followed=author).count()
            fields = {
                'author_name': author.name,
                'author_id': author.id,
                'follower_count': count,
            }

            serializers.influx_insert_internal({
                'measurement': 'author_follower',
                'fields': fields
            })

        return Response(serializer.data)


class ActiveUserNotificationsView(base_views.ListAPIView):
    model = models.UserNotification
    serializer_class = serializers.ActiveUserNotificationSerializer
    view_name = 'my_notifications_list'

    def get_queryset(self):
        obj = self.model.objects.filter(
            user=self.request.user
        )
        return obj


class ActiveUserNotificationsDetailView(
        base_views.RetrieveUpdateDestroyAPIView):

    model = models.UserNotification
    serializer_class = serializers.ActiveUserNotificationSerializer
    view_name = 'my_notifications_detail'

    def get_queryset(self):
        obj = self.model.objects.filter(
            user=self.request.user,
        )
        return obj


class ActiveUserUnreadNotificationView(base_views.APIView):
    def get(self, request):
        count = models.UserNotification.objects.filter(
            user=request.user,
            seen=False,
        ).count()
        return Response({'count': count})


class ActiveUserClearNotificationView(base_views.APIView):
    def delete(self, request):
        deleted = models.UserNotification.objects.filter(
            user=request.user
        ).delete()

        return Response(deleted)

    def put(self, request):
        unread = models.UserNotification.objects.filter(
            user=request.user,
            seen=False
        )

        for x in unread:
            x.seen = True
            x.save()

        return Response({'cleared': len(unread)})
