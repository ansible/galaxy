# (c) 2012-2018, Ansible
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
from unittest import mock

from django.core.exceptions import ValidationError
from django.db.models.manager import Manager
from django.db.utils import DataError, IntegrityError
from django.test import TestCase

import pytest

from galaxy.main.models import Tag
from galaxy.common.testing import NOW, LATER


class TagModelTest(TestCase):
    VALID_NAME = "NAME"

    NAME_MAX_LENGTH = 512

    def setUp(self):
        Tag.objects.all().delete()

    def test_manager_class(self):
        assert isinstance(Tag.objects, Manager)

    @pytest.mark.model_fields_validation
    @mock.patch('django.utils.timezone.now', side_effect=[NOW, NOW, LATER])
    def test_create_minimal(self, fake_now):
        # no mandatory fields
        tag = Tag.objects.create()
        assert isinstance(tag, Tag)

        # check defaults
        assert tag.name == ""
        assert tag.created == NOW
        assert tag.modified == NOW

        tag.save()
        assert tag.modified != NOW
        assert tag.modified == LATER
        assert fake_now.call_count == 3

    @pytest.mark.model_fields_validation
    def test_name_is_required(self):
        # does not raise
        Tag(name=self.VALID_NAME).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Tag().full_clean()

        assert excinfo.value.message_dict == {
            'name': ['This field cannot be blank.']
        }

    @pytest.mark.database_integrity
    def test_name_must_be_unique_in_db(self):

        with pytest.raises(IntegrityError) as excinfo:
            Tag.objects.create(name=self.VALID_NAME)
            Tag.objects.create(name=self.VALID_NAME)

        assert str(excinfo.value) == (
            'duplicate key value violates unique constraint '
            '"main_tag_name_key"\n'
            'DETAIL:  Key (name)=({duplicated_name}) already exists.\n'
        ).format(
            duplicated_name=self.VALID_NAME
        )

    @pytest.mark.database_integrity
    def test_name_length_is_limited_in_db(self):
        # does not raise
        Tag.objects.create(
            name='*' * self.NAME_MAX_LENGTH)

        with pytest.raises(DataError) as excinfo:
            Tag.objects.create(
                name='*' * (self.NAME_MAX_LENGTH + 1)
            )

        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
        ).format(
            max_allowed=self.NAME_MAX_LENGTH
        )

    @pytest.mark.model_fields_validation
    def test_name_length_is_limited(self):
        # does not raise
        Tag(name=self.VALID_NAME).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Tag(name='*' * (self.NAME_MAX_LENGTH + 1)).full_clean()

        assert excinfo.value.message_dict == {
            'name': [
                'Ensure this value has at most {valid} '
                'characters (it has {given}).'.format(
                    valid=self.NAME_MAX_LENGTH,
                    given=self.NAME_MAX_LENGTH + 1
                )
            ]
        }

    # testing custom methods

    @pytest.mark.model_methods
    def test_convert_to_string(self):
        # __str__ will return name
        tag = Tag(name=self.VALID_NAME)

        assert str(tag) == self.VALID_NAME

    @pytest.mark.model_methods
    def test_repr(self):
        # __str__ returns name, but it did not affected __repr__
        tag = Tag(name=self.VALID_NAME)

        assert repr(tag) == (
            '<Tag: {name}>'
            .format(name=self.VALID_NAME))

    @pytest.mark.model_methods
    def test_get_absolute_url(self):
        # this method creates url with tag id
        tag = Tag.objects.create(name=self.VALID_NAME)

        assert tag.get_absolute_url() == (
            "/api/v1/tags/{tag_id}/"
            .format(tag_id=tag.id))
