from django.conf import settings
from django.db import models

from galaxy.main import fields
from .base import PrimordialModel
from .importing import ImportTask


class NotificationSecret(PrimordialModel):
    class Meta:
        ordering = ('source', 'github_user', 'github_repo')
        unique_together = ('source', 'github_user', 'github_repo')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notification_secrets',
        db_index=True,
        on_delete=models.CASCADE,
    )
    source = models.CharField(
        max_length=20,
        verbose_name="Source"
    )
    github_user = models.CharField(
        max_length=256,
        verbose_name="Github Username",
    )
    github_repo = models.CharField(
        max_length=256,
        verbose_name="Github Repository",
    )
    secret = models.CharField(
        max_length=256,
        verbose_name="Secret",
        db_index=True
    )

    def __str__(self):
        return "{}-{}".format(self.owner.username, self.source)

    def repo_full_name(self):
        return "{}/{}".format(self.github_user, self.github_repo)


class Notification(PrimordialModel):
    class Meta:
        ordering = ('-id',)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        db_index=True,
        editable=False,
        on_delete=models.CASCADE,
    )
    source = models.CharField(
        max_length=20,
        verbose_name="Source",
        editable=False
    )
    github_branch = models.CharField(
        max_length=256,
        verbose_name="GitHub Branch",
        blank=True,
        editable=False
    )
    travis_build_url = models.CharField(
        max_length=256,
        blank=True
    )
    travis_status = models.CharField(
        max_length=256,
        blank=True
    )
    commit = models.CharField(
        max_length=256,
        blank=True
    )
    committed_at = models.DateTimeField(
        auto_now=False,
        null=True
    )
    commit_message = fields.TruncatingCharField(
        max_length=256,
        blank=True,
        default=''
    )
    repository = models.ForeignKey(
        'Repository',
        related_name='notifications',
        editable=False,
        on_delete=models.CASCADE,
    )
    import_task = models.ForeignKey(
        ImportTask,
        related_name='notifications',
        verbose_name='Tasks',
        editable=False,
        on_delete=models.CASCADE,
    )
