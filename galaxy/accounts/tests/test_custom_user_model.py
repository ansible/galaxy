# -*- coding: utf-8 -*-
# (c) 2012-2018, Ansible
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
from django.contrib.auth.models import UserManager
from django.db.utils import DataError, IntegrityError
from django.utils import timezone
from django.test import TestCase

import mock
import pytest

from galaxy.accounts.models import CustomUser
from galaxy.common.testing import NOW


class CustomUserModelTest(TestCase):
    VALID_EMAIL = "user@example.com"
    VALID_PASSWORD = "****"
    VALID_USERNAME = "USERNAME"

    USERNAME_MAX_LENGTH = 30
    FULL_NAME_MAX_LENGTH = 254
    SHORT_NAME_MAX_LENGTH = 30
    EMAIL_MAX_LENGTH = 254

    def setUp(self):
        CustomUser.objects.all().delete()

    def test_manager_class(self):
        assert isinstance(CustomUser.objects, UserManager)

    def test_default(self):
        assert CustomUser._meta.get_field('date_joined').default == \
            timezone.now

    @pytest.mark.model_fields_validation
    @mock.patch.object(
        CustomUser._meta.get_field('date_joined'),
        "get_default",
        side_effect=[NOW])
    def test_create_minimal(self, fake_now):
        # no mandatory fields
        user = CustomUser.objects.create()
        assert isinstance(user, CustomUser)

        # check defaults
        assert user.username == ""
        assert user.full_name == ""
        assert user.short_name == ""
        assert not user.is_staff
        assert user.email == ""
        assert user.is_active
        assert user.date_joined == NOW
        assert user.karma == 0
        assert user.avatar_url == ""
        assert not user.cache_refreshed

        fake_now.assert_called_once()

    @pytest.mark.database_integrity
    def test_username_length_is_limited_in_db(self):
        # does not raise
        CustomUser.objects.create(
            username='*' * self.USERNAME_MAX_LENGTH)

        with pytest.raises(DataError) as excinfo:
            CustomUser.objects.create(
                username='*' * (self.USERNAME_MAX_LENGTH + 1))
        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
            .format(max_allowed=self.USERNAME_MAX_LENGTH))

    @pytest.mark.database_integrity
    def test_username_must_be_unique_in_db(self):
        duplicated_name = 'duplicated_name'
        with pytest.raises(IntegrityError) as excinfo:
            CustomUser.objects.create(username=duplicated_name)
            CustomUser.objects.create(username=duplicated_name)
        assert str(excinfo.value) == (
            'duplicate key value violates unique constraint '
            '"accounts_customuser_username_key"\n'
            'DETAIL:  Key (username)=({duplicated_name}) already exists.\n'
            .format(duplicated_name=duplicated_name))

    @pytest.mark.model_fields_validation
    def test_username_must_match_regex(self):
        # does not raise
        CustomUser(
            username='Abc',
            password=self.VALID_PASSWORD,
            email=self.VALID_EMAIL).full_clean()

        # does not raise
        CustomUser(
            username='A',
            password=self.VALID_PASSWORD,
            email=self.VALID_EMAIL).full_clean()

        # does not raise
        CustomUser(
            username='007',
            password=self.VALID_PASSWORD,
            email=self.VALID_EMAIL).full_clean()

        # does not raise
        CustomUser(
            username='@',
            password=self.VALID_PASSWORD,
            email=self.VALID_EMAIL).full_clean()

        # does not raise
        CustomUser(
            username='+++',
            password=self.VALID_PASSWORD,
            email=self.VALID_EMAIL).full_clean()

        # does not raise
        CustomUser(
            username='---',
            password=self.VALID_PASSWORD,
            email=self.VALID_EMAIL).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            CustomUser(
                username='',
                password=self.VALID_PASSWORD,
                email=self.VALID_EMAIL).full_clean()
        assert str(excinfo.value) == (
            "{'username': [u'This field cannot be blank.']}")

        with pytest.raises(ValidationError) as excinfo:
            CustomUser(
                username='~',
                password=self.VALID_PASSWORD,
                email=self.VALID_EMAIL).full_clean()
        assert str(excinfo.value) == (
            "{'username': [u'Enter a valid username.']}")

        with pytest.raises(ValidationError) as excinfo:
            CustomUser(
                username='$',
                password=self.VALID_PASSWORD,
                email=self.VALID_EMAIL).full_clean()
        assert str(excinfo.value) == (
            "{'username': [u'Enter a valid username.']}")

        with pytest.raises(ValidationError) as excinfo:
            CustomUser(
                username='"',
                password=self.VALID_PASSWORD,
                email=self.VALID_EMAIL).full_clean()
        assert str(excinfo.value) == (
            "{'username': [u'Enter a valid username.']}")

        with pytest.raises(ValidationError) as excinfo:
            CustomUser(
                username=u'юникод',
                password=self.VALID_PASSWORD,
                email=self.VALID_EMAIL).full_clean()
        assert str(excinfo.value) == (
            "{'username': [u'Enter a valid username.']}")

        with pytest.raises(ValidationError) as excinfo:
            CustomUser(
                username=u'юникод',
                password=self.VALID_PASSWORD,
                email=self.VALID_EMAIL).full_clean()
        assert str(excinfo.value) == (
            "{'username': [u'Enter a valid username.']}")

    @pytest.mark.database_integrity
    def test_full_name_length_is_limited_in_db(self):
        # does not raise
        CustomUser.objects.create(
            full_name='*' * self.FULL_NAME_MAX_LENGTH)

        with pytest.raises(DataError) as excinfo:
            CustomUser.objects.create(
                full_name='*' * (self.FULL_NAME_MAX_LENGTH + 1))
        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
            .format(max_allowed=self.FULL_NAME_MAX_LENGTH))

    @pytest.mark.model_fields_validation
    def test_full_name_length_is_limited(self):
        # does not raise
        CustomUser(
            username=self.VALID_USERNAME,
            password=self.VALID_PASSWORD,
            email=self.VALID_EMAIL,
            full_name='*' * self.EMAIL_MAX_LENGTH).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            CustomUser(
                username=self.VALID_USERNAME,
                password=self.VALID_PASSWORD,
                email=self.VALID_EMAIL,
                full_name='*' * (self.EMAIL_MAX_LENGTH + 1)).full_clean()
        assert str(excinfo.value) == (
            "{'full_name': [u'Ensure this value has at most 254 "
            "characters (it has 255).']}")

    @pytest.mark.database_integrity
    def test_short_name_length_is_limited_in_db(self):
        # does not raise
        CustomUser.objects.create(
            short_name='*' * self.SHORT_NAME_MAX_LENGTH)

        with pytest.raises(DataError) as excinfo:
            CustomUser.objects.create(
                short_name='*' * (self.SHORT_NAME_MAX_LENGTH + 1))
        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
            .format(max_allowed=self.SHORT_NAME_MAX_LENGTH))

    @pytest.mark.database_integrity
    def test_email_length_is_limited_in_db(self):
        # does not raise
        CustomUser.objects.create(
            email='*' * self.EMAIL_MAX_LENGTH)

        with pytest.raises(DataError) as excinfo:
            CustomUser.objects.create(
                email='*' * (self.EMAIL_MAX_LENGTH + 1))
        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
            .format(max_allowed=self.EMAIL_MAX_LENGTH))

    # testing custom methods

    @pytest.mark.model_methods
    def test_convert_to_string(self):
        # __str__ will return username
        user = CustomUser(
            username=self.VALID_USERNAME,
            password=self.VALID_PASSWORD,
            email=self.VALID_EMAIL)

        assert str(user) == self.VALID_USERNAME

    @pytest.mark.model_methods
    def test_repr(self):
        # __str__ returns username, but it did not affected __repr__
        user = CustomUser(
            username=self.VALID_USERNAME,
            password=self.VALID_PASSWORD,
            email=self.VALID_EMAIL)

        assert repr(user) == (
            '<CustomUser: {username}>'
            .format(username=self.VALID_USERNAME))

    @pytest.mark.model_methods
    def test_get_full_name(self):
        # this method strips whitespaces from full name
        user = CustomUser(
            full_name="Full name")
        assert user.get_full_name() == "Full name"

        user = CustomUser(
            full_name="Full name with trailing spaces         ")
        assert user.get_full_name() == "Full name with trailing spaces"

        user = CustomUser(
            full_name="Full name with newlines \n\n\n")
        assert user.get_full_name() == "Full name with newlines"

    @pytest.mark.model_methods
    def test_get_short_name(self):
        # this method strips whitespaces from short name
        user = CustomUser(
            short_name="Short name")
        assert user.get_short_name() == "Short name"

        user = CustomUser(
            short_name="Short name with trailing spaces         ")
        assert user.get_short_name() == "Short name with trailing spaces"

        user = CustomUser(
            short_name="Short name with newlines \n\n\n")
        assert user.get_short_name() == "Short name with newlines"

    @pytest.mark.model_methods
    def test_get_absolute_url(self):
        # this method creates url with urlencoded username
        user = CustomUser(
            username=self.VALID_USERNAME)

        assert user.get_absolute_url() == (
            '/users/{username}/'
            .format(username=self.VALID_USERNAME))

        user = CustomUser(
            username="Aaa123@")
        assert user.get_absolute_url() == (
            '/users/Aaa123%40/')
