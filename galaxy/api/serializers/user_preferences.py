import logging

from rest_framework import serializers
from .serializers import BaseSerializer
from galaxy.main import models


logger = logging.getLogger(__name__)

__all__ = [
    'ActiveUserPreferencesSerializer',
]


class ActiveUserPreferencesSerializer(BaseSerializer):
    preferences = serializers.JSONField()

    class Meta:
        model = models.UserPreferences
        fields = (
            'preferences',
            'repositories_followed',
            'namespaces_followed'
        )

    def get_summary_fields(self, obj):
        followed_repos = []
        for repo in obj.repositories_followed.all():
            followed_repos.append({
                'id': repo.id,
                'name': repo.name,
                'namespace': repo.provider_namespace.namespace.name,
                'description': repo.description,
                'avatar': repo.provider_namespace.namespace.avatar_url
            })

        followed_ns = []
        for ns in obj.namespaces_followed.all():
            followed_ns.append({
                'id': ns.id,
                'name': ns.name,
                'description': ns.description,
                'avatar': ns.avatar_url
            })

        return {
            'repositories_followed': followed_repos,
            'namespaces_followed': followed_ns
        }
