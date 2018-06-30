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

import enum

import pytest

from galaxy.common import schema


class Color(enum.Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'


class TestEnum(object):

    def test_serialize(self):
        field = schema.Enum(Color)
        assert field.serialize('attr', {'attr': Color.RED}) == 'red'
        assert field.serialize('attr', {'attr': Color.GREEN}) == 'green'
        assert field.serialize('attr', {'attr': Color.BLUE}) == 'blue'

    def test_serialize_allow_none(self):
        field = schema.Enum(Color, allow_none=True)
        assert field.serialize('attr', {'attr': None}) is None

    def test_serialize_str(self):
        field = schema.Enum(Color)
        assert field.serialize('attr', {'attr': 'red'}) == 'red'
        assert field.serialize('attr', {'attr': 'green'}) == 'green'
        assert field.serialize('attr', {'attr': 'blue'}) == 'blue'

    def test_serialize_fail(self):
        field = schema.Enum(Color)
        with pytest.raises(ValueError):
            field.serialize('attr', {'attr': 'magenta'})

    def test_deserialize(self):
        field = schema.Enum(Color)
        assert field.deserialize('red') is Color.RED
        assert field.deserialize('green') is Color.GREEN
        assert field.deserialize('blue') is Color.BLUE

    def test_deserialize_fail(self):
        field = schema.Enum(Color)
        with pytest.raises(ValueError):
            field.deserialize('magenta')
