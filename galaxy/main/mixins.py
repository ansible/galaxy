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


__all__ = ['DirtyMixin',]

###################################################################################
# A mixin object that lets us check if a model object has been modified

class DirtyMixin(object):
    def __init__(self, *args, **kwargs):
        super(DirtyMixin, self).__init__(*args, **kwargs)
        self._original_state = dict(self.__dict__)

    @property
    def is_dirty(self):
        missing = object()
        for key, value in self._original_state.iteritems():
            if value != self.__dict__.get(key, missing):
                return True
        return False

    def save(self, *args, **kwargs):
        state = dict(self.__dict__)
        del state['_original_state']
        self._original_state = state
        super(DirtyMixin, self).save()

