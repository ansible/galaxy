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
import re

import attr
from marshmallow import fields
import semantic_version as semver

from galaxy import constants


class Enum(fields.Field):
    def __init__(self, enum, *args, **kwargs):
        super(Enum, self).__init__(*args, **kwargs)
        self.enum = enum

    def _deserialize(self, value, attr, data):
        return self.enum(value)

    def _serialize(self, value, attr, obj):
        if self.allow_none and value is None:
            return None
        return self.enum(value).value


_FILENAME_RE = re.compile(
    r'^(?P<namespace>\w+)-(?P<name>\w+)-'
    r'(?P<version>[0-9a-zA-Z.+-]+)\.tar\.gz$'
)


@attr.s(slots=True)
class CollectionFilename(object):

    namespace = attr.ib()
    name = attr.ib()
    version = attr.ib(converter=semver.Version)

    @classmethod
    def parse(cls, filename):
        match = _FILENAME_RE.match(filename)
        if not match:
            raise ValueError(
                'Invalid filename. Expected: '
                '{namespace}-{name}-{version}.tar.gz'
            )

        return cls(**match.groupdict())

    @namespace.validator
    @name.validator
    def _validator(self, attribute, value):
        if not constants.NAME_REGEXP.match(value):
            raise ValueError(
                'Invalid {0}: {1!r}'.format(attribute.name, value)
            )
