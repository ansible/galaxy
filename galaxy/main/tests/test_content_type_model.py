# -*- coding: utf-8 -*-
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

from django.core.exceptions import ValidationError
from django.db.models.manager import Manager
from django.db.utils import DataError, IntegrityError
from django.test import TestCase

import mock
import pytest

from galaxy.main.models import ContentType
from galaxy.common.testing import NOW, LATER
from galaxy import constants


class ContentTypeModelTest(TestCase):
    VALID_NAME_ENUM = constants.ContentType.ROLE
    VALID_NAME = constants.ContentType.ROLE.value
    VALID_NAME_OTHER = constants.ContentType.MODULE.value
    VALID_DESCRIPTION = "DESCRIPTION"

    NAME_MAX_LENGTH = 512
    DESCRIPTION_MAX_LENGTH = 255

    def setUp(self):
        ContentType.objects.all().delete()

    def test_manager_class(self):
        assert isinstance(ContentType.objects, Manager)

    @pytest.mark.model_fields_validation
    @mock.patch('django.utils.timezone.now', side_effect=[NOW, NOW, LATER])
    def test_create_minimal(self, fake_now):
        # no mandatory fields
        content_type = ContentType.objects.create()
        assert isinstance(content_type, ContentType)

        # check defaults
        assert content_type.name == ""
        assert content_type.created == NOW
        assert content_type.modified == NOW

        content_type.save()
        assert content_type.modified != NOW
        assert content_type.modified == LATER
        assert fake_now.call_count == 3

    @pytest.mark.model_fields_validation
    def test_name_is_required(self):
        # does not raise
        ContentType(name=self.VALID_NAME).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            ContentType().full_clean()

        assert str(excinfo.value) == (
            "{'name': [u'This field cannot be blank.']}"
        )
        assert str(excinfo.value) == str({
            "name": [
                u"This field cannot be blank."
            ]
        })

    @pytest.mark.database_integrity
    def test_name_must_be_unique_in_db(self):

        with pytest.raises(IntegrityError) as excinfo:
            ContentType.objects.create(name=self.VALID_NAME)
            ContentType.objects.create(name=self.VALID_NAME)

        assert str(excinfo.value) == (
            'duplicate key value violates unique constraint '
            '"main_contenttype_name_key"\n'
            'DETAIL:  Key (name)=({duplicated_name}) already exists.\n'
        ).format(
            duplicated_name=self.VALID_NAME
        )

    @pytest.mark.database_integrity
    def test_name_length_is_limited_in_db(self):
        # does not raise
        ContentType.objects.create(
            name='*' * self.NAME_MAX_LENGTH
        )

        with pytest.raises(DataError) as excinfo:
            ContentType.objects.create(
                name='*' * (self.NAME_MAX_LENGTH + 1)
            )

        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
        ).format(
            max_allowed=self.NAME_MAX_LENGTH
        )

    @pytest.mark.model_fields_validation
    def test_name_is_limited_to_choices(self):
        # does not raise
        ContentType(name=self.VALID_NAME).full_clean()
        invald_name = 'INVALID NAME'

        assert invald_name not in constants.ContentType.choices()

        with pytest.raises(ValidationError) as excinfo:
            ContentType(name=invald_name).full_clean()

        assert str(excinfo.value) == str({
            "name": [
                (
                    u"Value \'{given}\' is not a valid choice."
                ).format(
                    given=invald_name
                )
            ]
        })

    @pytest.mark.model_fields_validation
    def test_description_is_not_required(self):
        # does not raise
        ContentType(name=self.VALID_NAME).full_clean()

    @pytest.mark.database_integrity
    def test_description_may_not_be_unique_in_db(self):

        # does not raise
        ContentType.objects.create(
            name=self.VALID_NAME,
            description=self.VALID_DESCRIPTION,
        )
        ContentType.objects.create(
            name=self.VALID_NAME_OTHER,
            description=self.VALID_DESCRIPTION,
        )

    @pytest.mark.database_integrity
    def test_description_length_is_limited_in_db(self):
        # does not raise
        ContentType.objects.create(
            name=self.VALID_NAME,
            description='a' * self.DESCRIPTION_MAX_LENGTH
        )

        # does not raise
        content_type = ContentType.objects.create(
            name=self.VALID_NAME_OTHER,
            description='b' * (self.DESCRIPTION_MAX_LENGTH + 1)
        )

        # ..but truncated
        content_type = ContentType.objects.get(id=content_type.id)

        assert len(content_type.description) == self.DESCRIPTION_MAX_LENGTH
        assert content_type.description == (
            'b' * (self.DESCRIPTION_MAX_LENGTH - 3) + '...'
        )

    @pytest.mark.model_fields_validation
    def test_description_length_is_limited(self):
        # does not raise
        ContentType(
            name=self.VALID_NAME,
            description='a' * self.DESCRIPTION_MAX_LENGTH
        ).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            ContentType(
                name=self.VALID_NAME_OTHER,
                description='a' * (self.DESCRIPTION_MAX_LENGTH + 1)
            ).full_clean()

        assert str(excinfo.value) == str({
            "description": [
                (
                    u"Ensure this value has at most {valid} characters "
                    "(it has {given})."
                ).format(
                    valid=self.DESCRIPTION_MAX_LENGTH,
                    given=self.DESCRIPTION_MAX_LENGTH + 1
                )
            ]
        })

    # testing custom methods

    @pytest.mark.model_methods
    def test_convert_to_string(self):
        # __str__ will return name
        content_type = ContentType(name=self.VALID_NAME)

        assert str(content_type) == self.VALID_NAME

    @pytest.mark.model_methods
    def test_repr(self):
        # __str__ returns name, but it did not affected __repr__
        content_type = ContentType(name=self.VALID_NAME)

        assert repr(content_type) == (
            '<ContentType: {name}>'
        ).format(name=self.VALID_NAME)

    @pytest.mark.model_methods
    def test_get_absolute_url(self):
        # this method creates url with content_type id
        content_type = ContentType.objects.create(name=self.VALID_NAME)

        assert content_type.get_absolute_url() == (
            "/api/v1/content_types/{content_type_id}/"
        ).format(content_type_id=content_type.id)

    @pytest.mark.model_methods
    def test_classmethod_get(self):
        # this is a shortener for model.objects.get() for enums
        content_type = ContentType.objects.create(name=self.VALID_NAME)

        assert ContentType.get(self.VALID_NAME_ENUM).id == content_type.id
        assert ContentType.get(self.VALID_NAME_ENUM.value).id == \
            content_type.id

        with pytest.raises(ContentType.DoesNotExist) as excinfo:
            assert ContentType.get(self.VALID_NAME_OTHER)

        assert str(excinfo.value) == str(
            "ContentType matching query does not exist."
        )
