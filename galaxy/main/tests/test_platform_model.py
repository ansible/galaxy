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
from django.db.utils import DataError
from django.test import TestCase

import mock
import pytest

from galaxy.main.models import Platform
from galaxy.common.testing import NOW, LATER


class PlatformModelTest(TestCase):
    VALID_NAME = "NAME"
    VALID_RELEASE = "RELEASE"
    VALID_ALIAS = "ALIAS"

    NAME_MAX_LENGTH = 512
    RELEASE_MAX_LENGTH = 50
    ALIAS_MAX_LENGTH = 256

    def setUp(self):
        Platform.objects.all().delete()

    def test_manager_class(self):
        assert isinstance(Platform.objects, Manager)

    @pytest.mark.model_fields_validation
    @mock.patch('django.utils.timezone.now', side_effect=[NOW, NOW, LATER])
    def test_create_minimal(self, fake_now):
        # no mandatory fields
        platform = Platform.objects.create()
        assert isinstance(platform, Platform)

        # check defaults
        assert platform.name == ""
        assert platform.created == NOW
        assert platform.modified == NOW

        platform.save()
        assert platform.modified != NOW
        assert platform.modified == LATER
        assert fake_now.call_count == 3

    @pytest.mark.model_fields_validation
    def test_name_and_release_are_required(self):
        # does not raise
        Platform(
            name=self.VALID_NAME,
            release=self.VALID_RELEASE
        ).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Platform().full_clean()

        assert excinfo.value.message_dict == {
            'release': ['This field cannot be blank.'],
            'name': ['This field cannot be blank.']
        }

    # FIXME: This behaviour looks like a bug
    @pytest.mark.database_integrity
    def test_platform_duplicates_are_allowed(self):
        # does not raise
        Platform.objects.create(
            name=self.VALID_NAME,
            release=self.VALID_RELEASE,
            alias=self.VALID_ALIAS
        )
        Platform.objects.create(
            name=self.VALID_NAME,
            release=self.VALID_RELEASE,
            alias=self.VALID_ALIAS
        )

    @pytest.mark.database_integrity
    def test_name_length_is_limited_in_db(self):
        # does not raise
        Platform.objects.create(
            name='*' * self.NAME_MAX_LENGTH,
            release=self.VALID_RELEASE
        )

        with pytest.raises(DataError) as excinfo:
            Platform.objects.create(
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
        Platform(
            name=self.VALID_NAME,
            release=self.VALID_RELEASE
        ).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Platform(
                name='*' * (self.NAME_MAX_LENGTH + 1),
                release=self.VALID_RELEASE
            ).full_clean()

        assert excinfo.value.message_dict == {
            'name': [
                'Ensure this value has at most {valid} '
                'characters (it has {given}).'.format(
                    valid=self.NAME_MAX_LENGTH,
                    given=self.NAME_MAX_LENGTH + 1
                )
            ]
        }

    @pytest.mark.database_integrity
    def test_release_length_is_limited_in_db(self):
        # does not raise
        Platform.objects.create(
            name=self.VALID_NAME,
            release='*' * self.RELEASE_MAX_LENGTH
        )

        with pytest.raises(DataError) as excinfo:
            Platform.objects.create(
                name=self.VALID_NAME,
                release='*' * (self.RELEASE_MAX_LENGTH + 1)
            )

        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
        ).format(
            max_allowed=self.RELEASE_MAX_LENGTH
        )

    @pytest.mark.model_fields_validation
    def test_release_length_is_limited(self):
        # does not raise
        Platform(
            name=self.VALID_NAME,
            release='*' * self.RELEASE_MAX_LENGTH).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Platform(
                name=self.VALID_NAME,
                release='*' * (self.RELEASE_MAX_LENGTH + 1)).full_clean()
        assert excinfo.value.message_dict == {
            'release': [
                "Ensure this value has at most {valid} "
                "characters (it has {given}).".format(
                    valid=self.RELEASE_MAX_LENGTH,
                    given=self.RELEASE_MAX_LENGTH + 1
                )
            ]
        }

    @pytest.mark.database_integrity
    def test_alias_length_is_limited_in_db(self):
        # does not raise
        Platform.objects.create(
            name=self.VALID_NAME,
            release=self.VALID_RELEASE,
            alias='*' * self.ALIAS_MAX_LENGTH)

        with pytest.raises(DataError) as excinfo:
            Platform.objects.create(
                name=self.VALID_NAME,
                release=self.VALID_RELEASE,
                alias='*' * (self.ALIAS_MAX_LENGTH + 1)
            )

        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
        ).format(
            max_allowed=self.ALIAS_MAX_LENGTH
        )

    @pytest.mark.model_fields_validation
    def test_alias_length_is_limited(self):
        # does not raise
        Platform(
            name=self.VALID_NAME,
            release=self.VALID_RELEASE,
            alias='*' * self.ALIAS_MAX_LENGTH
        ).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Platform(
                name=self.VALID_NAME,
                release=self.VALID_RELEASE,
                alias='*' * (self.ALIAS_MAX_LENGTH + 1)).full_clean()
        assert excinfo.value.message_dict == {
            'alias': [
                'Ensure this value has at most {valid} '
                'characters (it has {given}).'.format(
                    valid=self.ALIAS_MAX_LENGTH,
                    given=self.ALIAS_MAX_LENGTH + 1
                )
            ]
        }

    # testing custom methods

    @pytest.mark.model_methods
    def test_convert_to_string(self):
        # __str__ will return name-release
        platform = Platform(
            name=self.VALID_NAME,
            release=self.VALID_RELEASE
        )

        assert str(platform) == self.VALID_NAME + "-" + self.VALID_RELEASE

    @pytest.mark.model_methods
    def test_repr(self):
        # __str__ returns name, but and it affects __repr__
        platform = Platform(
            name=self.VALID_NAME,
            release=self.VALID_RELEASE)

        assert repr(platform) == (
            '<Platform: {name}-{release}>'
        ).format(
            name=self.VALID_NAME,
            release=self.VALID_RELEASE
        )

    @pytest.mark.model_methods
    def test_get_absolute_url(self):
        # this method creates url with platform id
        platform = Platform.objects.create(name=self.VALID_NAME)

        assert platform.get_absolute_url() == (
            "/api/v1/platforms/{platform_id}/"
        ).format(
            platform_id=platform.id
        )
