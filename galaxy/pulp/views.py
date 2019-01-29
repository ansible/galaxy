from pulpcore.app.viewsets import TaskViewSet as _TaskViewSet
from rest_framework.permissions import IsAuthenticated

from . import serializers


class TaskViewSet(_TaskViewSet):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.TaskSerializer
