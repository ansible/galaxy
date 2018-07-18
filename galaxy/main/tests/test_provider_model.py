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

from galaxy.main.models import Provider
from galaxy.common.testing import NOW, LATER


class ProviderModelTest(TestCase):
    VALID_NAME = "NAME"
    # FIXME: Need to be validated
    VALID_DOWNLOAD_URL = "URL"

    NAME_MAX_LENGTH = 512
    DOWNLOAD_URL_MAX_LENGTH = 256

    def setUp(self):
        Provider.objects.all().delete()

    def test_manager_class(self):
        assert isinstance(Provider.objects, Manager)

    @pytest.mark.model_fields_validation
    @mock.patch('django.utils.timezone.now', side_effect=[NOW, NOW, LATER])
    def test_create_minimal(self, fake_now):
        # no mandatory fields
        provider = Provider.objects.create()
        assert isinstance(provider, Provider)

        # check defaults
        assert provider.name == ""
        assert provider.created == NOW
        assert provider.modified == NOW
        assert provider.download_url is None

        provider.save()
        assert provider.modified != NOW
        assert provider.modified == LATER
        assert fake_now.call_count == 3

    @pytest.mark.model_fields_validation
    def test_name_is_required(self):
        # does not raise
        Provider(
            name=self.VALID_NAME,
            download_url=self.VALID_DOWNLOAD_URL
        ).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Provider(
                download_url=self.VALID_DOWNLOAD_URL
            ).full_clean()

        assert str(excinfo.value) == (
            "{'name': [u'This field cannot be blank.']}"
        )

    @pytest.mark.database_integrity
    def test_name_must_be_unique_in_db(self):
        duplicated_name = 'duplicated_name'
        with pytest.raises(IntegrityError) as excinfo:
            Provider.objects.create(name=duplicated_name)
            Provider.objects.create(name=duplicated_name)
        assert str(excinfo.value) == (
            'duplicate key value violates unique constraint '
            '"main_provider_name_key"\n'
            'DETAIL:  Key (name)=({duplicated_name}) already exists.\n'
        ).format(
            duplicated_name=duplicated_name
        )

    # FIXME: Looks like a bug
    @pytest.mark.model_fields_validation
    def test_download_must_not_be_unique_in_db(self):
        # does not raise
        Provider(
            name=self.VALID_NAME,
            download_url=self.VALID_DOWNLOAD_URL
        ).full_clean()

        # does not raise
        Provider(
            name=self.VALID_NAME + "_",
            download_url=self.VALID_DOWNLOAD_URL
        ).full_clean()

    @pytest.mark.database_integrity
    def test_name_length_is_limited_in_db(self):
        # does not raise
        Provider.objects.create(
            name='*' * self.NAME_MAX_LENGTH,
            download_url=self.VALID_DOWNLOAD_URL
        )

        with pytest.raises(DataError) as excinfo:
            Provider.objects.create(
                name='*' * (self.NAME_MAX_LENGTH + 1),
                download_url=self.VALID_DOWNLOAD_URL
            )

        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
        ).format(max_allowed=self.NAME_MAX_LENGTH)

    @pytest.mark.model_fields_validation
    def test_name_length_is_limited(self):
        # does not raise
        Provider(
            name=self.VALID_NAME,
            download_url=self.VALID_DOWNLOAD_URL
        ).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Provider(
                name='*' * (self.NAME_MAX_LENGTH + 1),
                download_url=self.VALID_DOWNLOAD_URL
            ).full_clean()

        assert str(excinfo.value) == (
            "{{'name': [u'Ensure this value has at most {valid} "
            "characters (it has {current}).']}}"
        ).format(
            valid=self.NAME_MAX_LENGTH,
            current=self.NAME_MAX_LENGTH + 1
        )

    @pytest.mark.model_fields_validation
    def test_name_is_not_validated(self):
        # does not raise
        Provider(
            name="!@#$%^&*(",
            download_url=self.VALID_DOWNLOAD_URL
        ).full_clean()

    @pytest.mark.database_integrity
    def test_download_url_length_is_limited_in_db(self):
        # does not raise
        Provider.objects.create(
            name=self.VALID_NAME,
            download_url='*' * (self.DOWNLOAD_URL_MAX_LENGTH)
        )

        with pytest.raises(DataError) as excinfo:
            Provider.objects.create(
                name=self.VALID_NAME,
                download_url='*' * (self.DOWNLOAD_URL_MAX_LENGTH + 1)
            )

        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
        ).format(max_allowed=self.DOWNLOAD_URL_MAX_LENGTH)

    @pytest.mark.model_fields_validation
    def test_download_url_length_is_limited(self):
        # does not raise
        Provider(
            name=self.VALID_NAME,
            download_url='*' * self.DOWNLOAD_URL_MAX_LENGTH
        ).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Provider(
                name=self.VALID_NAME,
                download_url='*' * (self.DOWNLOAD_URL_MAX_LENGTH + 1)
            ).full_clean()

        assert str(excinfo.value) == (
            "{{'download_url': [u'Ensure this value has at most {valid} "
            "characters (it has {current}).']}}"
        ).format(
            valid=self.DOWNLOAD_URL_MAX_LENGTH,
            current=self.DOWNLOAD_URL_MAX_LENGTH + 1
        )

    @pytest.mark.model_fields_validation
    def test_download_url_is_not_validated(self):
        # does not raise
        Provider(
            name=self.VALID_NAME,
            download_url='!@#$%^&*()'
        ).full_clean()

    # testing custom methods

    @pytest.mark.model_methods
    def test_convert_to_string(self):
        # __str__ will return name
        provider = Provider.objects.create(
            name=self.VALID_NAME,
            download_url=self.VALID_DOWNLOAD_URL
        )

        assert str(provider) == (
            "{name}-{provider_id}"
        ).format(
            name=self.VALID_NAME,
            provider_id=provider.id
        )

    @pytest.mark.model_methods
    def test_repr(self):
        # __str__ returns name, but it did not affected __repr__
        provider = Provider.objects.create(
            name=self.VALID_NAME,
            download_url=self.VALID_DOWNLOAD_URL
        )

        assert repr(provider) == (
            '<Provider: {name}-{provider_id}>'
        ).format(
            name=self.VALID_NAME,
            provider_id=provider.id
        )

    @pytest.mark.model_methods
    def test_get_absolute_url(self):
        # this method creates url with provider id
        provider = Provider.objects.create(
            name=self.VALID_NAME,
            download_url=self.VALID_DOWNLOAD_URL
        )

        # TODO: WHy active? There is no inactive field on model.
        # this should be documented
        assert provider.get_absolute_url() == (
            "/api/v1/providers/active/{provider_id}/"
        ).format(
            provider_id=provider.id
        )
