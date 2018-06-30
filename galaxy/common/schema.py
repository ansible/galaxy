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

from marshmallow import fields


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
