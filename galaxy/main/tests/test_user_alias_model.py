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

import pytest

from galaxy.main.models import UserAlias
from galaxy.accounts.models import CustomUser


class TestUserAliasModel(TestCase):
    VALID_ALIAS_NAME = "NAME"

    ALIAS_NAME_MAX_LENGTH = 30

    def setUp(self):
        CustomUser.objects.all().delete()
        UserAlias.objects.all().delete()

        self.default_user = CustomUser.objects.create(
            username="USER",
            email="user@example.com"
        )
        self.another_user = CustomUser.objects.create(
            username="OTHER",
            email="other@example.com"
        )

    def test_manager_class(self):
        assert isinstance(UserAlias.objects, Manager)

    @pytest.mark.model_fields_validation
    def test_create_minimal(self):
        # no mandatory fields, except fk
        user_alias = UserAlias.objects.create(
            alias_of=self.default_user
        )
        assert isinstance(user_alias, UserAlias)

        # check fk
        assert isinstance(user_alias.alias_of, CustomUser)
        assert user_alias.alias_of.pk == self.default_user.pk

        # check defaults
        assert user_alias.alias_name == ""

    @pytest.mark.model_fields_validation
    def test_alis_name_is_required(self):

        with pytest.raises(ValidationError) as excinfo:
            UserAlias(
                alias_of=self.default_user
            ).full_clean()

        assert excinfo.value.message_dict == {
            'alias_name': ['This field cannot be blank.']
        }

    @pytest.mark.skip
    @pytest.mark.database_integrity
    def test_alias_of_is_required_in_db(self):
        with pytest.raises(IntegrityError) as excinfo:
            UserAlias.objects.create(
                alias_name=self.VALID_ALIAS_NAME,
                alias_of=self.default_user
            )

        assert str(excinfo.value) == (
            'null value in column "alias_of_id" violates not-null constraint '
            'DETAIL:  Failing row contains ({alias_pk}, {alias_name}, null)\n'
        ).format(
            # FIXME: get correct pk or filter out alias_pk from error
            alias_pk=4,
            alias_name=self.VALID_ALIAS_NAME
        )

    @pytest.mark.database_integrity
    def test_alias_name_must_be_unique_in_db(self):

        with pytest.raises(IntegrityError) as excinfo:
            UserAlias.objects.create(
                alias_name=self.VALID_ALIAS_NAME,
                alias_of=self.default_user
            )
            UserAlias.objects.create(
                alias_name=self.VALID_ALIAS_NAME,
                alias_of=self.another_user
            )
        assert str(excinfo.value) == (
            'duplicate key value violates unique constraint '
            '"main_useralias_alias_name_key"\n'
            'DETAIL:  Key (alias_name)=({duplicated_name}) already exists.\n'
        ).format(
            duplicated_name=self.VALID_ALIAS_NAME
        )

    @pytest.mark.database_integrity
    def test_alias_of_may_not_be_unique_for_same_user_in_db(self):
        # does not raise
        UserAlias.objects.create(
            alias_name=self.VALID_ALIAS_NAME,
            alias_of=self.default_user
        )
        UserAlias.objects.create(
            alias_name=self.VALID_ALIAS_NAME + "a",
            alias_of=self.default_user
        )

    @pytest.mark.database_integrity
    def test_alias_of_must_be_unique_for_different_users_in_db(self):

        with pytest.raises(IntegrityError) as excinfo:
            UserAlias.objects.create(
                alias_name=self.VALID_ALIAS_NAME,
                alias_of=self.default_user
            )
            UserAlias.objects.create(
                alias_name=self.VALID_ALIAS_NAME,
                alias_of=self.another_user
            )

        assert str(excinfo.value) == (
            'duplicate key value violates unique constraint '
            '"main_useralias_alias_name_key"\n'
            'DETAIL:  Key (alias_name)=({duplicated_name}) already exists.\n'
        ).format(
            duplicated_name=self.VALID_ALIAS_NAME
        )

    @pytest.mark.database_integrity
    def test_alias_of_may_not_be_unique_in_db(self):
        # does not raise
        UserAlias.objects.create(
            alias_name=self.VALID_ALIAS_NAME,
            alias_of=self.default_user
        )
        UserAlias.objects.create(
            alias_name=self.VALID_ALIAS_NAME + "a",
            alias_of=self.default_user
        )

    @pytest.mark.database_integrity
    def test_alias_name_length_is_limited_in_db(self):
        # does not raise
        UserAlias.objects.create(
            alias_name='*' * self.ALIAS_NAME_MAX_LENGTH,
            alias_of=self.default_user
        )

        with pytest.raises(DataError) as excinfo:
            UserAlias.objects.create(
                alias_name='*' * (self.ALIAS_NAME_MAX_LENGTH + 1),
                alias_of=self.another_user
            )

        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
        ).format(max_allowed=self.ALIAS_NAME_MAX_LENGTH)

    # testing custom methods

    @pytest.mark.model_methods
    def test_convert_to_string(self):
        # __str__ will return name
        user_alias = UserAlias(
            alias_name=self.VALID_ALIAS_NAME,
            alias_of=self.default_user
        )

        assert str(user_alias) == (
            "{alias_name} (alias of {user_name})"
        ).format(
            alias_name=self.VALID_ALIAS_NAME,
            user_name=self.default_user.username
        )

    @pytest.mark.model_methods
    def test_repr(self):
        # __str__ returns name, but it did not affected __repr__
        user_alias = UserAlias(
            alias_name=self.VALID_ALIAS_NAME,
            alias_of=self.default_user
        )

        assert repr(user_alias) == (
            '<UserAlias: {alias_name} (alias of {user_name})>'
        ).format(
            alias_name=self.VALID_ALIAS_NAME,
            user_name=self.default_user.username
        )

    @pytest.mark.model_methods
    def test_fails_to_get_absolute_url(self):
        # this is very uncommon, but this model does not have an url
        user_alias = UserAlias(
            alias_name=self.VALID_ALIAS_NAME,
            alias_of=self.default_user
        )
        with pytest.raises(AttributeError) as excinfo:
            user_alias.get_absolute_url()

        assert str(excinfo.value) == (
            "'UserAlias' object has no attribute 'get_absolute_url'"
        )
