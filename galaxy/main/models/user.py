from django.conf import settings
from django.contrib.postgres import fields as psql_fields
from django.db import models

from .base import BaseModel, PrimordialModel
from .repository import Repository


class UserPreferences(BaseModel):

    DEFAULT_PREFERENCES = {
        # Notify me when a user adds a survey for my content.
        'notify_survey': False,
        'ui_notify_survey': True,

        # Notify me when an import fails.
        'notify_import_fail': True,
        'ui_notify_import_fail': True,

        # Notify me when an import succeeds.
        'notify_import_success': False,
        'ui_notify_import_success': True,

        # Notify me when a new release is available for content I'm following.
        'notify_content_release': True,
        'ui_notify_content_release': True,

        # Notify me when an author I'm following creates new content.
        'notify_author_release': True,
        'ui_notify_author_release': True,

        # Notify me when there is a Galaxy announcement.
        'notify_galaxy_announce': True,
        'ui_notify_galaxy_announce': True,
    }

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True
    )

    # DEFAULT_PREFERENCES dict cannot be used as a default value
    # for preferences fieldto avoid sharing reference to mutable dict
    # accross model instances.
    # Django suggests using calables to generate copies of default value
    # for JSON field, but since there is no known way how to bind that exeact
    # value to a migration, it should be avoided.
    # Therefore preferences field is initialized in model `__init__()` method
    # and updated when constructed from the database in `from_db()` method.
    preferences = psql_fields.JSONField(
        null=False,
        default=dict,
    )

    repositories_followed = models.ManyToManyField(
        'main.Repository',
        editable=True,
        blank=True
    )

    collections_followed = models.ManyToManyField(
        'main.Collection',
        editable=True,
        blank=True
    )

    namespaces_followed = models.ManyToManyField(
        'main.Namespace',
        editable=True,
        blank=True
    )

    def __init__(self, *args, **kwargs):
        super(UserPreferences, self).__init__(*args, **kwargs)
        self.update_defaults()

    def __str__(self):
        return self.user.username

    @classmethod
    def from_db(cls, db, field_names, values):
        new = super(UserPreferences, cls).from_db(db, field_names, values)
        new.update_defaults()
        return new

    def update_defaults(self):
        """
        Add any preferences that are in default preferences but missing from
        the user's preferences to the user's preferences.
        """
        for key in set(self.DEFAULT_PREFERENCES) - set(self.preferences):
            self.preferences[key] = self.DEFAULT_PREFERENCES[key]


class UserAlias(models.Model):
    """
    A class representing a mapping between users and aliases to allow
    for user renaming without breaking deps.
    """

    class Meta:
        verbose_name_plural = "UserAliases"

    alias_of = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='aliases',
        on_delete=models.CASCADE,
    )
    alias_name = models.CharField(
        # must be in-sync with galaxy/accounts/models.py:CustomUser
        max_length=30,
        unique=True,
    )

    def __str__(self):
        return '{} (alias of {})'.format(
            self.alias_name, self.alias_of.username)


class UserNotification(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    repository = models.ForeignKey(
        Repository,
        on_delete=models.SET_NULL,
        null=True
    )

    message = models.CharField(
        max_length=512
    )

    type = models.CharField(
        max_length=128
    )

    seen = models.BooleanField(
        default=False
    )


class Subscription(PrimordialModel):
    class Meta:
        unique_together = ('owner', 'github_user', 'github_repo')
        ordering = ('owner', 'github_user', 'github_repo')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )
    # TODO(cutwater): Replace with reference to a Repository model
    github_user = models.CharField(
        max_length=256,
        verbose_name="Github Username",
    )
    github_repo = models.CharField(
        max_length=256,
        verbose_name="Github Repository",
    )
