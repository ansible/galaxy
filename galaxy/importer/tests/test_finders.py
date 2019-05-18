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

import unittest
from unittest import mock

import pytest

from galaxy import constants
from galaxy.importer import exceptions as exc
from galaxy.importer import finders


class TestApbFinder(unittest.TestCase):

    def setUp(self):
        path_exists_mock = mock.patch('os.path.exists')
        self.path_exists_mock = path_exists_mock.start()
        self.addCleanup(path_exists_mock.stop)

    def test_find_content(self):
        temp_dir = '/tmp/i63AJuQQex'
        existing_path = '/tmp/i63AJuQQex/apb.yaml'

        def path_exists(path):
            return path == existing_path

        self.path_exists_mock.side_effect = path_exists

        finder = finders.ApbFinder(temp_dir)
        contents = list(finder.find_contents())

        assert len(contents) == 1
        assert contents[0] == finders.Result(
            content_type=constants.ContentType.APB,
            path='',
            extra={'metadata_path': '/tmp/i63AJuQQex/apb.yaml'}
        )

    def test_find_content_fail(self):
        temp_dir = '/tmp/i63AJuQQex'
        self.path_exists_mock.return_value = False

        finder = finders.ApbFinder(temp_dir)

        with pytest.raises(exc.ContentNotFound):
            finder.find_contents()


class TestRoleFinder(unittest.TestCase):

    def setUp(self):
        path_exists = mock.patch('os.path.exists')
        self.path_exists_mock = path_exists.start()
        self.addCleanup(path_exists.stop)

    def test_find_content(self):
        temp_dir = '/tmp/hTmTxgljOw'
        existing_path = '/tmp/hTmTxgljOw/meta/main.yaml'

        def path_exists(path):
            return path == existing_path
        self.path_exists_mock.side_effect = path_exists

        finder = finders.RoleFinder(temp_dir)
        contents = list(finder.find_contents())

        assert len(contents) == 1
        assert contents[0] == finders.Result(
            content_type=constants.ContentType.ROLE,
            path='',
            extra={'metadata_path': '/tmp/hTmTxgljOw/meta/main.yaml'}
        )

    def test_find_content_fail(self):
        temp_dir = '/tmp/hTmTxgljOw'
        self.path_exists_mock.return_value = False

        finder = finders.RoleFinder(temp_dir)

        with pytest.raises(exc.ContentNotFound):
            finder.find_contents()


class TestFileSystemFinder(unittest.TestCase):

    def test_find_content(self):
        pytest.xfail('Not implemented')

    def test_find_content_fail(self):
        pytest.xfail('Not implemented')


class TestMetadataFinder(unittest.TestCase):

    def test_find_content(self):
        pytest.xfail('Not implemented')

    def test_find_content_fail(self):
        pytest.xfail('Not implemented')
