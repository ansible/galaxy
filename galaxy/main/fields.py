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

import json

from distutils.version import LooseVersion
import psycopg2.extras

from django.contrib.postgres import lookups
from django.core import exceptions
from django.db import models
from django.utils.translation import ugettext_lazy as _


__all__ = [
    'LooseVersionField',
    'TruncatingCharField',
    'JSONField'
]


class LooseVersionField(models.Field):
    """ store and return values as a LooseVersion """

    def db_type(self, connection):
        return 'varchar(64)'

    def get_internal_type(self):
        return 'CharField'

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def to_python(self, value):
        return LooseVersion(value)

    def get_prep_value(self, value):
        return str(value)


# From: http://stackoverflow.com/questions/3459843/auto-truncating-fields-at-max-length-in-django-charfields
class TruncatingCharField(models.CharField):
    def get_prep_value(self, value):
        value = super(TruncatingCharField, self).get_prep_value(value)
        if value and len(value) > self.max_length:
            return value[:self.max_length - 3] + '...'
        return value


# NOTE(cutwater): JSONField is implemented in Django since version 1.9.
# This is a backport of JSONField from Django 1.9.13 that should be removed
# after upgrade to the higher version of Django.
class JSONField(models.Field):
    empty_strings_allowed = False
    description = _('A JSON object')
    default_error_messages = {
        'invalid': _("Value must be valid JSON."),
    }

    def db_type(self, connection):
        return 'jsonb'

    def get_transform(self, name):
        transform = super(JSONField, self).get_transform(name)
        if transform:
            return transform
        return KeyTransformFactory(name)

    def get_prep_value(self, value):
        if value is not None:
            return psycopg2.extras.Json(value)
        return value

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type in ('has_key', 'has_keys', 'has_any_keys'):
            return value
        if isinstance(value, (dict, list)):
            return psycopg2.extras.Json(value)
        return super(JSONField, self).get_prep_lookup(lookup_type, value)

    def validate(self, value, model_instance):
        super(JSONField, self).validate(value, model_instance)
        try:
            json.dumps(value)
        except TypeError:
            raise exceptions.ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': value},
            )

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return value


class HasKey(lookups.PostgresSimpleLookup):
    lookup_name = 'has_key'
    operator = '?'


class HasKeys(lookups.PostgresSimpleLookup):
    lookup_name = 'has_keys'
    operator = '?&'


class HasAnyKeys(lookups.PostgresSimpleLookup):
    lookup_name = 'has_any_keys'
    operator = '?|'


JSONField.register_lookup(lookups.DataContains)
JSONField.register_lookup(lookups.ContainedBy)
JSONField.register_lookup(HasKey)
JSONField.register_lookup(HasKeys)
JSONField.register_lookup(HasAnyKeys)


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
