from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from pulpcore.app import models as pulp_models

from galaxy import constants
from .base import PrimordialModel


class ImportTask(PrimordialModel):
    class Meta:
        ordering = ('-id',)
        get_latest_by = 'created'

    # TODO(cutwater): Constants left for backward compatibility, to be removed
    STATE_PENDING = constants.ImportTaskState.PENDING.value
    STATE_RUNNING = constants.ImportTaskState.RUNNING.value
    STATE_FAILED = constants.ImportTaskState.FAILED.value
    STATE_SUCCESS = constants.ImportTaskState.SUCCESS.value

    # collection related
    artifact = models.ForeignKey(
        pulp_models.Artifact,
        # artifact can be deleted if import not successful
        db_constraint=False,
        related_name='import_tasks',
        on_delete=models.SET_NULL,
        null=True,
    )
    collection = models.ForeignKey(
        'Collection',
        related_name='import_tasks',
        on_delete=models.CASCADE,
        null=True,
    )

    repository = models.ForeignKey(
        'Repository',
        related_name='import_tasks',
        on_delete=models.CASCADE,
        null=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='import_tasks',
        db_index=True,
        on_delete=models.CASCADE,
    )
    import_branch = models.CharField(
        max_length=256,
        null=True,
        blank=False,
    )
    celery_task_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    state = models.CharField(
        max_length=20,
        default=STATE_PENDING,
        choices=constants.ImportTaskState.choices()
    )
    started = models.DateTimeField(
        auto_now_add=False,
        null=True,
        blank=True,
    )
    finished = models.DateTimeField(
        auto_now_add=False,
        null=True,
        blank=True,
    )

    # GitHub repo attributes at time of import
    commit = models.CharField(
        max_length=256,
        blank=True
    )
    commit_message = models.CharField(
        max_length=256,
        blank=True
    )
    commit_url = models.CharField(
        max_length=256,
        blank=True
    )
    travis_status_url = models.CharField(
        max_length=256,
        blank=True,
        default='',
        verbose_name="Travis Build Status"
    )
    travis_build_url = models.CharField(
        max_length=256,
        blank=True,
        default='',
        verbose_name="Travis Build URL"
    )

    def __str__(self):
        return '{}-{}'.format(self.id, self.state)

    def start(self):
        self.state = ImportTask.STATE_RUNNING
        self.started = timezone.now()
        self.save()

    def finish_success(self, message=None):
        self.state = ImportTask.STATE_SUCCESS
        self.finished = timezone.now()
        if message:
            self.messages.create(message_type=ImportTaskMessage.TYPE_SUCCESS,
                                 message_text=message)
        self.save()

    def finish_failed(self, reason=None):
        self.state = ImportTask.STATE_FAILED
        self.finished = timezone.now()
        if reason:
            # FIXME(cutwater): Remove truncating reason to 256 chars.
            # Use TruncatingCharField or TextField for message field
            self.messages.create(message_type=ImportTaskMessage.TYPE_FAILED,
                                 message_text=str(reason)[:256])
        self.save()


class ImportTaskMessage(PrimordialModel):
    TYPE_INFO = constants.ImportTaskMessageType.INFO.value
    TYPE_WARNING = constants.ImportTaskMessageType.WARNING.value
    TYPE_SUCCESS = constants.ImportTaskMessageType.SUCCESS.value
    # FIXME(cutwater): ERROR and FAILED types seem to be redundant
    TYPE_FAILED = constants.ImportTaskMessageType.FAILED.value
    TYPE_ERROR = constants.ImportTaskMessageType.ERROR.value

    task = models.ForeignKey(
        ImportTask,
        related_name='messages',
        on_delete=models.CASCADE,
    )
    content = models.ForeignKey(
        'Content',
        related_name='messages',
        null=True,
        on_delete=models.CASCADE,
    )
    message_type = models.CharField(
        max_length=10,
        choices=constants.ImportTaskMessageType.choices(),
    )
    message_text = models.TextField()
    is_linter_rule_violation = models.NullBooleanField(
        default=False,
    )
    linter_type = models.CharField(
        max_length=25,
        null=True,
    )
    linter_rule_id = models.CharField(
        max_length=50,
        null=True,
    )
    content_name = models.CharField(
        max_length=256,
        null=True,
    )
    rule_desc = models.TextField(
        null=True,
    )
    rule_severity = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        null=True,
    )
    score_type = models.CharField(
        max_length=25,
        null=True,
    )

    def __str__(self):
        return "{}-{}-{}".format(
            self.task.id, self.message_type, self.message_text)
