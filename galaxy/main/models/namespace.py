# (c) 2012-2019, Ansible by Red Hat
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by
# the Apache Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Apache License for more details.
#
# You should have received a copy of the Apache License
# along with Galaxy.  If not, see <http://www.apache.org/licenses/>.

from django.conf import settings
from django.db import models
from django.urls import reverse

from .base import CommonModel
from .content import Content


class Namespace(CommonModel):
    """
    Represents the aggregation of multiple namespaces across providers.
    """

    class Meta:
        ordering = ('name',)

    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='namespaces',
        editable=True,
    )
    avatar_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Avatar URL"
    )
    location = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Location"
    )
    company = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Company Name"
    )
    email = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Email Address"
    )
    html_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Web Site URL"
    )

    is_vendor = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('api:namespace_detail', args=(self.pk,))

    @property
    def content_counts(self):
        return Content.objects \
            .filter(namespace=self.pk) \
            .values('content_type__name') \
            .annotate(count=models.Count('content_type__name')) \
            .order_by('content_type__name')

    def is_owner(self, user):
        return self.owners.filter(pk=user.pk).exists()
