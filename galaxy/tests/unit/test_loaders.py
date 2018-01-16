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

import unittest
import mock

from galaxy.main import constants
from galaxy.worker import loaders
from galaxy.worker.loaders import role as role_loader


class TestRoleMetaParser(unittest.TestCase):

    def setUp(self):
        log_mock = mock.patch('galaxy.worker.loaders.role.LOG')
        self.log = log_mock.start()
        self.addCleanup(log_mock.stop)

    def test_parse_tags(self):
        parser = role_loader.RoleMetaParser({
            'galaxy_tags': ['database', 'sql']
        })
        tags = parser.parse_tags()
        self.assertListEqual(tags, ['database', 'sql'])

    def test_parse_tags_invalid(self):
        parser = role_loader.RoleMetaParser({
            'galaxy_tags': ['database', 's q l']
        })
        tags = parser.parse_tags()
        self.assertListEqual(tags, ['database'])
        self.log.warn.assert_called_once_with(
            '"s q l" is not a valid tag. Skipping.')

    def test_parse_categories(self):
        parser = role_loader.RoleMetaParser({
            'categories': ['database', 'sql'],
        })
        tags = parser.parse_tags()
        self.assertListEqual(tags, ['database', 'sql'])
        self.log.warn.assert_called_once_with(
            'Found "categories" in metadata. Update the metadata '
            'to use "galaxy_tags" rather than categories.')

    def test_parse_platforms(self):
        parser = role_loader.RoleMetaParser({
            'platforms': [
                {'name': 'Ubuntu', 'versions': ['trusty', 'xenial']},
                {'name': 'RHEL', 'versions': ['all']}
            ]
        })
        platforms = parser.parse_platforms()
        self.assertListEqual(platforms, [
            role_loader.PlatformInfo('Ubuntu', ['trusty', 'xenial']),
            role_loader.PlatformInfo('RHEL', ['all'])
        ])

    def test_parse_cloud_platforms(self):
        parser = role_loader.RoleMetaParser({
            'cloud_platforms': ['AWX', 'OpenStack']
        })
        platforms = parser.parse_cloud_platforms()
        self.assertListEqual(platforms, ['AWX', 'OpenStack'])

    def test_parse_dependencies(self):
        pass

    def test_parse_videos(self):
        parser = role_loader.RoleMetaParser({
            'video_links': [{
                'title': 'Google Drive Video',
                'url': 'https://drive.google.com/file/d/gxH17k3EzzJP3g/browse'
            }, {
                'title': 'Vimeo Video',
                'url': 'https://vimeo.com/1733124',
            }, {
                'title': 'Youtube Video',
                'url': 'https://youtu.be/TxHPpfkGms9eDQ'
            }]
        })

        videos = parser.parse_videos()

        self.assertListEqual(videos, [
            role_loader.VideoLink(
                'https://drive.google.com/file/d/gxH17k3EzzJP3g/preview',
                'Google Drive Video'),
            role_loader.VideoLink(
                'https://player.vimeo.com/video/1733124',
                'Vimeo Video'),
            role_loader.VideoLink(
                'https://www.youtube.com/embed/TxHPpfkGms9eDQ',
                'Youtube Video'),
        ])


class TestRoleParser(unittest.TestCase):
    @mock.patch.object(loaders.RoleLoader, '_load_metadata')
    @mock.patch.object(loaders.RoleLoader, '_load_container_yml')
    def test_load_role(self, load_container_yml_mock, load_metadata_mock):
        load_metadata_mock.return_value = {
            'description': 'A test role',
            'author': 'John Smith',
            'min_ansible_version': '2.4.0',
        }
        load_container_yml_mock.return_value = (None, None)

        loader = loaders.RoleLoader('/tmp/repo/roles/test_role')
        role = loader.load()

        self.assertEqual(role.name, 'test_role')
        self.assertEqual(role.role_type, constants.RoleType.ANSIBLE)
        self.assertEqual(role.description, 'A test role')
        self.assertEqual(role.author, 'John Smith')
        self.assertEqual(role.min_ansible_version, '2.4.0')
        self.assertEqual(role.min_ansible_container_version, None)
