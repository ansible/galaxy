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
        return {}
