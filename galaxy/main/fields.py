# (c) 2012-2018, Ansible by Red Hat
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

import semver
import distutils.version

from django.db import models


__all__ = [
    'TruncatingCharField',
    'VersionField',
]


class VersionField(models.CharField):
    """Semantic version field."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 64)
        super(VersionField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return semver.parse_version_info(value)

    def to_python(self, value):
        if isinstance(value, semver.VersionInfo):
            return value
        if value is None:
            return value
        return semver.parse_version_info(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return str(value)


# TODO(cutwater): LooseVersionField is not used in actual models and is kept
# only because it's referenced by migration 0001_initial.py
class LooseVersionField(models.Field):
    """Store and return values as a LooseVersion."""

    def db_type(self, connection):
        return 'varchar(64)'

    def get_internal_type(self):
        return 'CharField'

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def to_python(self, value):
        return distutils.version.LooseVersion(value)

    def get_prep_value(self, value):
        return str(value)


# From: http://stackoverflow.com/questions/3459843/auto-truncating-fields-at-max-length-in-django-charfields # noqa: E501
class TruncatingCharField(models.CharField):
    def get_prep_value(self, value):
        value = super(TruncatingCharField, self).get_prep_value(value)
        if value and len(value) > self.max_length:
            return value[:self.max_length - 3] + '...'
        return value


class KeyTransform(models.Transform):

    def __init__(self, key_name, *args, **kwargs):
        super(KeyTransform, self).__init__(*args, **kwargs)
        self.key_name = key_name

    def as_sql(self, compiler, connection):
        key_transforms = [self.key_name]
        previous = self.lhs
        while isinstance(previous, KeyTransform):
            key_transforms.insert(0, previous.key_name)
            previous = previous.lhs
        lhs, params = compiler.compile(previous)
        if len(key_transforms) > 1:
            return "{} #> %s".format(lhs), [key_transforms] + params
        try:
            int(self.key_name)
        except ValueError:
            lookup = "'{}'".format(self.key_name)
        else:
            lookup = "{}".format(self.key_name)
        return "{} -> {}".format(lhs, lookup), params


class KeyTransformFactory(object):

    def __init__(self, key_name):
        self.key_name = key_name

    def __call__(self, *args, **kwargs):
        return KeyTransform(self.key_name, *args, **kwargs)
