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

from galaxy.main.models import ContentBlock
from galaxy.common.testing import NOW, LATER


class ContentBlockModelTest(TestCase):
    # letters, numbers, underscores or hyphens
    VALID_NAME = "NAME"
    VALID_CONTENT = "CONTENT"

    NAME_MAX_LENGTH = 50
    CONTENT_MAX_LENGTH = 512000

    def setUp(self):
        ContentBlock.objects.all().delete()

    def test_manager_class(self):
        assert isinstance(ContentBlock.objects, Manager)

    @pytest.mark.model_fields_validation
    @mock.patch('django.utils.timezone.now', side_effect=[NOW, NOW, LATER])
    def test_create_minimal(self, fake_now):
        # no mandatory fields
        content_block = ContentBlock.objects.create()
        assert isinstance(content_block, ContentBlock)

        # check defaults
        assert content_block.name == ""
        assert content_block.content == ""
        assert content_block.created == NOW
        assert content_block.modified == NOW

        content_block.save()
        assert content_block.modified != NOW
        assert content_block.modified == LATER
        assert fake_now.call_count == 3

    @pytest.mark.model_fields_validation
    def test_name_is_required(self):
        # does not raise
        ContentBlock(name=self.VALID_NAME).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            ContentBlock().full_clean()

        assert str(excinfo.value) == (
            "{'name': [u'This field cannot be blank.']}"
        )

    @pytest.mark.database_integrity
    def test_name_must_be_unique_in_db(self):

        with pytest.raises(IntegrityError) as excinfo:
            ContentBlock.objects.create(name=self.VALID_NAME)
            ContentBlock.objects.create(name=self.VALID_NAME)

        assert str(excinfo.value) == (
            'duplicate key value violates unique constraint '
            '"main_contentblock_name_key"\n'
            'DETAIL:  Key (name)=({duplicated_name}) already exists.\n'
        ).format(
            duplicated_name=self.VALID_NAME
        )

    @pytest.mark.database_integrity
    def test_name_length_is_limited_in_db(self):
        # does not raise
        ContentBlock.objects.create(
            name='*' * self.NAME_MAX_LENGTH
        )

        with pytest.raises(DataError) as excinfo:
            ContentBlock.objects.create(
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
        ContentBlock(name=self.VALID_NAME).full_clean()

        with pytest.raises(ValidationError) as excinfo:
            ContentBlock(name='a' * (self.NAME_MAX_LENGTH + 1)).full_clean()

        assert str(excinfo.value) == str({
            "name": [
                (
                    u"Ensure this value has at most {valid} characters "
                    "(it has {given})."
                ).format(
                    valid=self.NAME_MAX_LENGTH,
                    given=self.NAME_MAX_LENGTH + 1
                )
            ]
        })

    @pytest.mark.model_fields_validation
    def test_name_must_be_slug(self):
        # does not raise
        ContentBlock(name=self.VALID_NAME).full_clean()
        ContentBlock(name='name').full_clean()
        ContentBlock(name='na_me').full_clean()
        ContentBlock(name='Name').full_clean()
        ContentBlock(name='NamE').full_clean()
        ContentBlock(name='na-me').full_clean()
        ContentBlock(name='na-me-2').full_clean()

        with pytest.raises(ValidationError) as excinfo:
            ContentBlock(name='with spaces').full_clean()

        assert str(excinfo.value) == str({
            "name": [
                u"Enter a valid 'slug' consisting of letters, "
                "numbers, underscores or hyphens."
            ]
        })

        with pytest.raises(ValidationError) as excinfo:
            ContentBlock(name='with spaces').full_clean()

        assert str(excinfo.value) == str({
            "name": [
                u"Enter a valid 'slug' consisting of letters, "
                "numbers, underscores or hyphens."
            ]
        })

    @pytest.mark.model_fields_validation
    def test_content_is_unlimited(self):
        # does not raise
        ContentBlock(
            name=self.VALID_NAME,
            content='*' * 10000
        ).full_clean()

    # testing custom methods

    @pytest.mark.model_methods
    def test_convert_to_string(self):
        # __str__ will return name
        content_block = ContentBlock(name=self.VALID_NAME)

        assert str(content_block) == self.VALID_NAME

    @pytest.mark.model_methods
    def test_repr(self):
        # __str__ returns name, but it did not affected __repr__
        content_block = ContentBlock(name=self.VALID_NAME)

        assert repr(content_block) == (
            '<ContentBlock: {name}>'
            .format(name=self.VALID_NAME))

    @pytest.mark.model_methods
    def test_get_absolute_url(self):
        # this method creates url with content_block id
        content_block = ContentBlock.objects.create(name=self.VALID_NAME)

        assert content_block.get_absolute_url() == (
            "/api/v1/content_blocks/{content_block_name}/"
            .format(content_block_name=content_block.name))
