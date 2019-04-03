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

from django.db import models

from galaxy.main import fields
from galaxy.main.mixins import DirtyMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class BaseModel(models.Model, DirtyMixin):
    """Common model for objects not needing name, description,
    active attributes."""

    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        if hasattr(self, 'name'):
            return '{}-{}'.format(self.name, self.id)
        else:
            return '{}-{}'.format(self._meta.verbose_name, self.id)


class PrimordialModel(BaseModel):
    """Base model for CommonModel and CommonModelNameNotUnique."""

    class Meta:
        abstract = True

    description = fields.TruncatingCharField(
        max_length=255, blank=True, default='')
    active = models.BooleanField(default=True, db_index=True)


class CommonModel(PrimordialModel):
    """A base model where the name is unique."""

    class Meta:
        abstract = True

    name = models.CharField(max_length=512, unique=True, db_index=True)


class CommonModelNameNotUnique(PrimordialModel):
    """A base model where the name is not unique."""

    class Meta:
        abstract = True

    name = models.CharField(max_length=512, unique=False, db_index=True)


class SurveyBase(BaseModel):
    """This allows for us to split surveys into RepositorySurvey and
    CollectionSurvey without causing inconsistencies in the questions we ask
    user"""

    class Meta:
        abstract = True

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
