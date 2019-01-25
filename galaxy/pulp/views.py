from pulpcore.app.viewsets import TaskViewSet as _TaskViewSet
from rest_framework.permissions import IsAuthenticated


class TaskViewSet(_TaskViewSet):

    permission_classes = (IsAuthenticated, )
