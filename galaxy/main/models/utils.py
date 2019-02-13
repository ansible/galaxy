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
import uuid

from django.db import models
from django.urls import reverse

from .base import BaseModel, PrimordialModel


class ContentBlock(BaseModel):
    name = models.SlugField(unique=True)
    content = models.TextField('content', blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api:content_block_detail', args=(self.name,))


class RefreshRoleCount(PrimordialModel):
    state = models.CharField(
        max_length=20
    )
    passed = models.IntegerField(
        default=0,
        null=True
    )
    failed = models.IntegerField(
        default=0,
        null=True
    )
    deleted = models.IntegerField(
        default=0,
        null=True
    )
    updated = models.IntegerField(
        default=0,
        null=True
    )


class InfluxSessionIdentifier(BaseModel):

    session_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    def __str__(self):
        return str(self.session_id)
