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


__all__ = ['DirtyMixin']


class DirtyMixin(object):
    """
    A mixin object that lets us check if a model object has been modified.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_state = dict(self.__dict__)

    @property
    def is_dirty(self):
        missing = object()
        for key, value in self._original_state.items():
            if value != self.__dict__.get(key, missing):
                return True
        return False

    def save(self, *args, **kwargs):
        state = dict(self.__dict__)
        del state['_original_state']
        self._original_state = state
        super().save()
