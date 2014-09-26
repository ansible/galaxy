# (c) 2012-2014, Ansible, Inc. <support@ansible.com>
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (c) 2013 AnsibleWorks, Inc.
# All Rights Reserved.

from django.db import models
from south.modelsinspector import add_introspection_rules
from distutils.version import LooseVersion

__all__ = ['LooseVersionField', 'TruncatingCharField']

class LooseVersionField(models.Field):
    ''' store and return values as a LooseVersion '''

    def db_type(self, connection):
        return 'varchar(64)'

    def get_internal_type(self):
        return 'CharField'

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def to_python(self, value):
        try:
            return LooseVersion(value)
        except:
            return value

    def get_prep_value(self, value):
        return str(value)

add_introspection_rules([], ["^galaxy\.main\.fields\.LooseVersionField"])

# From:
# http://stackoverflow.com/questions/3459843/auto-truncating-fields-at-max-length-in-django-charfields
class TruncatingCharField(models.CharField):
    def get_prep_value(self, value):
        value = super(TruncatingCharField,self).get_prep_value(value)
        if value and len(value) > self.max_length:
            return value[:self.max_length-3] + '...'
        return value

add_introspection_rules([], ["^galaxy\.main\.fields\.TruncatingCharField"])

