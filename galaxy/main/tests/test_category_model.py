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

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db.models.manager import Manager
from django.db.utils import DataError, IntegrityError
from django.utils import timezone
from django.test import TestCase

import mock
import pytest

from galaxy.main.models import Category


class CategoryModelTest(TestCase):
    NOW = timezone.now()
    LATER = NOW + timedelta(hours=1)

    VALID_NAME = "NAME"

    NAME_MAX_LENGTH = 512

    def setUp(self):
        Category.objects.all().delete()

    def test_manager_class(self):
        assert isinstance(Category.objects, Manager)

    @pytest.mark.model_fields_validation
    @mock.patch('django.utils.timezone.now', side_effect=[NOW, NOW, LATER])
    def test_create_minimal(self, fake_now):
        # no mandatory fields
        category = Category.objects.create()
        assert isinstance(category, Category)

        # check defaults
        assert category.name == ""
        assert category.created == self.NOW
        assert category.modified == self.NOW

        category.save()
        assert category.modified != self.NOW
        assert category.modified == self.LATER
        assert fake_now.call_count == 3

    @pytest.mark.model_fields_validation
    def test_name_is_required(self):
        # does not raise
        Category(name=self.VALID_NAME).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Category().full_clean()
        assert str(excinfo.value) == (
            "{'name': [u'This field cannot be blank.']}")

    @pytest.mark.database_integrity
    def test_name_must_be_unique_in_db(self):
        duplicated_name = 'duplicated_name'
        with pytest.raises(IntegrityError) as excinfo:
            Category.objects.create(name=duplicated_name)
            Category.objects.create(name=duplicated_name)
        assert str(excinfo.value) == (
            'duplicate key value violates unique constraint '
            '"main_category_name_key"\n'
            'DETAIL:  Key (name)=({duplicated_name}) already exists.\n'
            .format(duplicated_name=duplicated_name))

    @pytest.mark.database_integrity
    def test_name_length_is_limited_in_db(self):
        # does not raise
        Category.objects.create(
            name='*' * self.NAME_MAX_LENGTH)

        with pytest.raises(DataError) as excinfo:
            Category.objects.create(
                name='*' * (self.NAME_MAX_LENGTH + 1))
        assert str(excinfo.value) == (
            'value too long for type character varying({max_allowed})\n'
            .format(max_allowed=self.NAME_MAX_LENGTH))

    @pytest.mark.model_fields_validation
    def test_name_length_is_limited(self):
        # does not raise
        Category(name=self.VALID_NAME).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            Category(name='*' * (self.NAME_MAX_LENGTH + 1)).full_clean()
        assert str(excinfo.value) == (
            "{{'name': [u'Ensure this value has at most {valid} "
            "characters (it has {current}).']}}"
            .format(
                valid=self.NAME_MAX_LENGTH,
                current=self.NAME_MAX_LENGTH + 1))

    # testing custom methods

    @pytest.mark.model_methods
    def test_convert_to_string(self):
        # __str__ will return name
        category = Category(name=self.VALID_NAME)

        assert str(category) == self.VALID_NAME

    @pytest.mark.model_methods
    def test_repr(self):
        # __str__ returns name, but it did not affected __repr__
        category = Category(name=self.VALID_NAME)

        assert repr(category) == (
            '<Category: {name}>'
            .format(name=self.VALID_NAME))

    @pytest.mark.model_methods
    def test_get_absolute_url(self):
        # this method creates url with category id
        category = Category.objects.create(name=self.VALID_NAME)

        assert category.get_absolute_url() == (
            "/api/v1/categories/{category_id}/"
            .format(category_id=category.id))
