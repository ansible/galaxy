# (c) 2012-2017, Ansible by Red Hat
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

import pkg_resources
import unittest
import mock

from galaxy.common import version


class TestGetVersion(unittest.TestCase):

    def setUp(self):
        self.get_distribution_mock = mock.patch(
            'pkg_resources.get_distribution').start()
        self.git_describe_mock = mock.patch(
            'subprocess.check_output').start()

    def test_release_version(self):
        self.git_describe_mock.return_value = 'v1.0.0'
        version_ = version.get_git_version()
        self.assertEqual(version_, '1.0.0')

        self.git_describe_mock.return_value = 'v2.3rc0'
        version_ = version.get_git_version()
        self.assertEqual(version_, '2.3rc0')

    def test_dev_version(self):
        self.git_describe_mock.return_value = 'v1.0.0'
        version_ = version.get_git_version()
        self.assertEqual(version_, '1.0.0')

        self.git_describe_mock.return_value = 'v2.3rc0'
        version_ = version.get_git_version()
        self.assertEqual(version_, '2.3rc0')

    def test_package_version(self):
        dist = self.get_distribution_mock.return_value
        dist.version = '1.0.0'
        self.assertEqual(version.get_package_version('test'), '1.0.0')

    def test_package_version_fallback(self):
        self.get_distribution_mock.side_effect = \
            pkg_resources.DistributionNotFound()
        self.git_describe_mock.return_value = '1.0.0'

        self.assertEqual(version.get_package_version('test'), '1.0.0')
        self.git_describe_mock.assert_called_once()
