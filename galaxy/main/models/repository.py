import operator

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse

from galaxy import constants
from galaxy.main import fields

from .base import BaseModel
from .provider import ProviderNamespace
from .content import Content


class Repository(BaseModel):
    class Meta:
        unique_together = [
            ('provider_namespace', 'name'),
            ('provider_namespace', 'original_name'),
        ]
        ordering = ('provider_namespace', 'name')

    # Foreign keys
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='repositories'
    )
    provider_namespace = models.ForeignKey(
        ProviderNamespace,
        related_name='repositories',
        on_delete=models.CASCADE,
    )
    readme = models.ForeignKey(
        'Readme',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    # Fields
    name = models.CharField(max_length=256)
    original_name = models.CharField(max_length=256, null=False)
    format = models.CharField(max_length=16, null=True,
                              choices=constants.RepositoryFormat.choices())
    description = fields.TruncatingCharField(
        max_length=255, blank=True, default='')
    import_branch = models.CharField(max_length=256, null=True)
    is_enabled = models.BooleanField(default=False)

    # Repository attributes
    commit = models.CharField(max_length=256, blank=True, default='')
    commit_message = fields.TruncatingCharField(
        max_length=256, blank=True, default='')
    commit_url = models.CharField(max_length=256, blank=True, default='')
    commit_created = models.DateTimeField(
        null=True, verbose_name="Last Commit DateTime")
    stargazers_count = models.IntegerField(default=0)
    watchers_count = models.IntegerField(default=0)
    forks_count = models.IntegerField(default=0)
    open_issues_count = models.IntegerField(default=0)
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
    issue_tracker_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Issue Tracker URL",
    )
    download_count = models.IntegerField(
        default=0
    )
    deprecated = models.BooleanField(
        default=False,
    )
    community_score = models.FloatField(
        null=True
    )
    community_survey_count = models.IntegerField(
        default=0
    )

    quality_score = models.FloatField(
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    quality_score_date = models.DateTimeField(
        null=True,
        verbose_name="DateTime last scored",
    )

    is_new = models.BooleanField(
        default=False,
    )

    @property
    def clone_url(self):
        return "https://github.com/{user}/{repo}.git".format(
            user=self.provider_namespace.name,
            repo=self.original_name
        )

    @property
    def github_user(self):
        return self.provider_namespace.name

    @property
    def github_repo(self):
        return self.original_name

    @property
    def content_counts(self):
        return Content.objects \
            .filter(repository=self.pk) \
            .values('content_type__name') \
            .annotate(count=models.Count('content_type__name')) \
            .order_by('content_type__name')

    def get_absolute_url(self):
        return reverse('api:repository_detail', args=(self.pk,))

    def get_download_url(self, ref=None):
        download_url = self.provider_namespace.provider.download_url

        if ref is None:
            last_version = self.last_version()
            if last_version:
                ref = last_version.tag
            else:
                ref = self.import_branch

        return download_url.format(
            username=self.provider_namespace.name,
            repository=self.original_name,
            ref=ref,
        )

    def all_versions(self):
        return sorted(self.versions.filter(version__isnull=False).all(),
                      key=operator.attrgetter('version'),
                      reverse=True)

    def last_version(self):
        versions = self.all_versions()
        if versions:
            return versions[0]
        return None


class RepositoryVersion(BaseModel):
    class Meta:
        unique_together = ('repository', 'version')

    repository = models.ForeignKey(
        'Repository',
        related_name='versions',
        on_delete=models.CASCADE
    )

    version = fields.VersionField(null=True)
    tag = models.CharField(max_length=64)
    commit_sha = models.CharField(max_length=40, null=True)
    commit_date = models.DateTimeField(null=True)

    def __str__(self):
        return "{}.{}-{}".format(
            self.content.namespace, self.content.name, self.version)


class CommunitySurvey(BaseModel):
    class Meta:
        unique_together = ('user', 'repository')

    repository = models.ForeignKey(
        Repository,
        null=False,
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        on_delete=models.CASCADE,
    )

    # Survey scores
    docs = models.IntegerField(
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    ease_of_use = models.IntegerField(
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    does_what_it_says = models.IntegerField(
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    works_as_is = models.IntegerField(
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    used_in_production = models.IntegerField(
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )


class Readme(BaseModel):
    class Meta:
        unique_together = ('repository', 'raw_hash')

    repository = models.ForeignKey(
        Repository,
        null=False,
        on_delete=models.CASCADE,
        related_name='+',
    )
    raw = models.TextField(null=False, blank=False)
    raw_hash = models.CharField(
        max_length=128, null=False, blank=False)
    mimetype = models.CharField(max_length=32, blank=False)
    html = models.TextField(null=False, blank=False)

    def safe_delete(self):
        ref_count = (
                Repository.objects.filter(readme=self).count()
                + Content.objects.filter(readme=self).count()
        )
        if ref_count:
            return False

        self.delete()
        return True


# TODO(cutwater): This model is probably obsolete and should be removed.
class Stargazer(BaseModel):
    class Meta:
        unique_together = ('owner', 'repository')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='starred',
        on_delete=models.CASCADE,
    )

    repository = models.ForeignKey(
        Repository,
        related_name='stars',
        on_delete=models.CASCADE,
    )
