from django.db import models
from django.urls import reverse

from .base import CommonModel, PrimordialModel


class Provider(CommonModel):
    """
    Valid SCM providers (e.g., GitHub, GitLab, etc.)
    """

    download_url = models.CharField(max_length=256, null=True)

    class Meta:
        ordering = ('name',)

    def get_absolute_url(self):
        return reverse('api:active_provider_detail', args=(self.pk,))


class ProviderNamespace(PrimordialModel):
    """
    A one-to-one mapping to namespaces within each provider.
    """

    class Meta:
        ordering = ('provider', 'name')
        unique_together = [
            ('provider', 'name'),
            ('namespace', 'provider', 'name'),
        ]

    name = models.CharField(
        max_length=256,
        verbose_name="Name",
        editable=True,
        null=False
    )
    namespace = models.ForeignKey(
        'Namespace',
        related_name='provider_namespaces',
        editable=False,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Namespace'
    )
    provider = models.ForeignKey(
        'Provider',
        related_name='provider_namespaces',
        editable=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Provider'
    )
    display_name = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Display Name"
    )
    avatar_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=True,
        verbose_name="Avatar URL"
    )
    location = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=True,
        verbose_name="Location"
    )
    company = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=True,
        verbose_name="Company Name"
    )
    email = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=True,
        verbose_name="Email Address"
    )
    html_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        editable=True,
        verbose_name="Web Site URL"
    )
    followers = models.IntegerField(
        null=True,
        editable=True,
        verbose_name="Followers"
    )

    def get_absolute_url(self):
        return reverse('api:provider_namespace_detail', args=(self.pk,))
