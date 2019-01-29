from gettext import gettext as _

from rest_framework import serializers

from pulpcore.app import models as pulp_models
from pulpcore.app import serializers as pulp_serializers


class TaskSerializer(pulp_serializers.ModelSerializer):
    _href = pulp_serializers.IdentityField(view_name='tasks-detail')
    job_id = serializers.UUIDField(
        help_text=_("ID of the job in rq."),
        read_only=True
    )
    state = serializers.CharField(
        help_text=_(
            "The current state of the task. The possible values include:"
            " 'waiting', 'skipped', 'running', 'completed',"
            " 'failed' and 'canceled'."),
        read_only=True
    )
    started_at = serializers.DateTimeField(
        help_text=_("Timestamp of the when this task started execution."),
        read_only=True
    )
    finished_at = serializers.DateTimeField(
        help_text=_("Timestamp of the when this task stopped execution."),
        read_only=True
    )
    non_fatal_errors = serializers.JSONField(
        help_text=_(
            "A JSON Object of non-fatal errors encountered during"
            " the execution of this task."),
        read_only=True
    )
    error = serializers.JSONField(
        help_text=_(
            "A JSON Object of a fatal error encountered during"
            " the execution of this task."),
        read_only=True
    )
    worker = pulp_serializers.RelatedField(
        help_text=_("The worker associated with this task."
                    " This field is empty if a worker is not yet assigned."),
        read_only=True,
        view_name='workers-detail'
    )
    parent = pulp_serializers.RelatedField(
        help_text=_("The parent task that spawned this task."),
        read_only=True,
        view_name='tasks-detail'
    )
    spawned_tasks = pulp_serializers.RelatedField(
        help_text=_("Any tasks spawned by this task."),
        many=True,
        read_only=True,
        view_name='tasks-detail'
    )
    progress_reports = pulp_serializers.ProgressReportSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = pulp_models.Task
        fields = pulp_serializers.ModelSerializer.Meta.fields + (
            'job_id', 'state', 'started_at', 'finished_at',
            'non_fatal_errors', 'error', 'worker', 'parent',
            'spawned_tasks', 'progress_reports')
