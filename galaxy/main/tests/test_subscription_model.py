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

from galaxy.main.models import Subscription
from galaxy.accounts.models import CustomUser
from galaxy.common.testing import NOW, LATER


class TestSubscriptionModel(TestCase):
    VALID_NAME = "NAME"
    # FIXME: Need to be validated
    VALID_DESCRIPTION = "DESCRIPTION"
    # FIXME: Need to be validated
    VALID_GITHUB_REPO = "GITHUB_REPO"
    # FIXME: Need to be validated
    VALID_GITHUB_USER = "GITHUB_USER"

    NAME_MAX_LENGTH = 512
    DESCRIPTION_MAX_LENGTH = 256
    GITHUB_REPO_MAX_LENGTH = 256
    GITHUB_USER_MAX_LENGTH = 256

    def setUp(self):
        Subscription.objects.all().delete()
        CustomUser.objects.all().delete()
        self.default_user = CustomUser.objects.create(username="user")

    def test_manager_class(self):
        assert isinstance(Subscription.objects, Manager)

    @pytest.mark.model_fields_validation
    @mock.patch('django.utils.timezone.now', side_effect=[NOW, NOW, LATER])
    def test_create_minimal(self, fake_now):
        # no mandatory fields except user
        subscription = Subscription.objects.create(owner=self.default_user)
        assert isinstance(subscription, Subscription)

        # check defaults
        assert subscription.owner.id == self.default_user.id
        assert isinstance(subscription.owner, CustomUser)
        assert subscription.description == ''
        assert subscription.created == NOW
        assert subscription.modified == NOW
        assert subscription.github_repo == ''
        assert subscription.github_user == ''

        subscription.save()
        assert subscription.modified != NOW
        assert subscription.modified == LATER
        assert fake_now.call_count == 3

        subscriptions = list(self.default_user.subscriptions.all())
        assert len(subscriptions) == 1
        assert subscriptions[0].id == subscription.id

    @pytest.mark.database_integrity
    def test_user_id_is_mandatory_in_db(self):
        with pytest.raises(IntegrityError) as excinfo:
            Subscription.objects.create()

        # TODO: add validation for full str, example:
        # IntegrityError: null value in column "owner_id" violates \
        # not-null constraint
        # DETAIL:  Failing row contains (1, , 2018-07-19 17:35:26.784425+00, \
        # 2018-07-19 17:35:26.784425+00, t, , , null).

        assert 'null value in column "owner_id" violates not-null constraint' \
            in str(excinfo.value)

    @pytest.mark.model_fields_validation
    def test_owner_is_required(self):
        # does not raise
        Subscription(
            owner=self.default_user,
            github_repo=self.VALID_GITHUB_REPO,
            github_user=self.VALID_GITHUB_USER
        ).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Subscription(
                github_repo=self.VALID_GITHUB_REPO,
                github_user=self.VALID_GITHUB_USER
            ).full_clean()

        assert excinfo.value.message_dict == {
            'owner': ['This field cannot be null.']
        }

    @pytest.mark.model_fields_validation
    def test_github_user_is_required(self):
        # does not raise
        Subscription(
            owner=self.default_user,
            github_repo=self.VALID_GITHUB_REPO,
            github_user=self.VALID_GITHUB_USER
        ).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Subscription(
                owner=self.default_user,
                github_repo=self.VALID_GITHUB_REPO,
            ).full_clean()

        assert excinfo.value.message_dict == {
            'github_user': ['This field cannot be blank.']
        }

    @pytest.mark.model_fields_validation
    def test_github_user_length_is_limited(self):
        # does not raise
        Subscription(
            owner=self.default_user,
            github_repo=self.VALID_GITHUB_REPO,
            github_user='A' * self.GITHUB_USER_MAX_LENGTH
        ).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Subscription(
                owner=self.default_user,
                github_repo=self.VALID_GITHUB_REPO,
                github_user='A' * (self.GITHUB_USER_MAX_LENGTH + 1)
            ).full_clean()

        assert excinfo.value.message_dict == {
            'github_user': [
                'Ensure this value has at most {valid} '
                'characters (it has {current}).'.format(
                    valid=self.GITHUB_USER_MAX_LENGTH,
                    current=self.GITHUB_USER_MAX_LENGTH + 1
                )
            ]
        }

    @pytest.mark.database_integrity
    def test_github_user_length_is_limited_in_db(self):
        # does not raise
        Subscription.objects.create(
            owner=self.default_user,
            github_repo=self.VALID_GITHUB_REPO,
            github_user='A' * self.GITHUB_USER_MAX_LENGTH
        )

        with pytest.raises(DataError) as excinfo:
            Subscription.objects.create(
                owner=self.default_user,
                github_repo=self.VALID_GITHUB_REPO,
                github_user='A' * (self.GITHUB_USER_MAX_LENGTH + 1)
            )

        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
        ).format(max_allowed=self.GITHUB_USER_MAX_LENGTH)

    @pytest.mark.model_fields_validation
    def test_github_repo_is_required(self):
        # does not raise
        Subscription(
            owner=self.default_user,
            github_repo=self.VALID_GITHUB_REPO,
            github_user=self.VALID_GITHUB_USER
        ).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Subscription(
                owner=self.default_user,
                github_user=self.VALID_GITHUB_USER
            ).full_clean()

        assert excinfo.value.message_dict == {
            'github_repo': ['This field cannot be blank.']
        }

    @pytest.mark.model_fields_validation
    def test_github_repo_length_is_limited(self):
        # does not raise
        Subscription(
            owner=self.default_user,
            github_repo='A' * self.GITHUB_REPO_MAX_LENGTH,
            github_user=self.VALID_GITHUB_USER,
        ).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Subscription(
                owner=self.default_user,
                github_repo='A' * (self.GITHUB_REPO_MAX_LENGTH + 1),
                github_user=self.VALID_GITHUB_USER,
            ).full_clean()

        assert excinfo.value.message_dict == {
            'github_repo': [
                'Ensure this value has at most {valid} '
                'characters (it has {current}).'.format(
                    valid=self.GITHUB_REPO_MAX_LENGTH,
                    current=self.GITHUB_REPO_MAX_LENGTH + 1
                )
            ]
        }

    @pytest.mark.database_integrity
    def test_github_repo_length_is_limited_in_db(self):
        # does not raise
        Subscription.objects.create(
            owner=self.default_user,
            github_repo='A' * self.GITHUB_REPO_MAX_LENGTH,
            github_user=self.VALID_GITHUB_USER,
        )

        with pytest.raises(DataError) as excinfo:
            Subscription.objects.create(
                owner=self.default_user,
                github_repo='A' * (self.GITHUB_REPO_MAX_LENGTH + 1),
                github_user=self.VALID_GITHUB_USER,
            )

        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
        ).format(max_allowed=self.GITHUB_REPO_MAX_LENGTH)

    # testing custom methods

    @pytest.mark.model_methods
    def test_convert_to_string(self):
        # __str__ will return subscription-<id>
        subscription = Subscription.objects.create(
            owner=self.default_user,
            github_repo=self.VALID_GITHUB_REPO,
            github_user=self.VALID_GITHUB_USER,
        )

        assert str(subscription) == (
            "subscription-{subscription_id}"
        ).format(
            subscription_id=subscription.id
        )

    @pytest.mark.model_methods
    def test_repr(self):
        # __str__ returns name, but it did not affected __repr__
        subscription = Subscription.objects.create(
            owner=self.default_user,
            github_repo=self.VALID_GITHUB_REPO,
            github_user=self.VALID_GITHUB_USER,
        )

        assert repr(subscription) == (
            '<Subscription: subscription-{subscription_id}>'
        ).format(
            subscription_id=subscription.id
        )

    @pytest.mark.model_methods
    def test_fails_to_get_absolute_url(self):
        # this is very uncommon, but this model does not have an url
        subscription = Subscription.objects.create(
            owner=self.default_user,
            github_repo=self.VALID_GITHUB_REPO,
            github_user=self.VALID_GITHUB_USER,
        )
        with pytest.raises(AttributeError) as excinfo:
            subscription.get_absolute_url()

        assert str(excinfo.value) == (
            "'Subscription' object has no attribute 'get_absolute_url'"
        )
