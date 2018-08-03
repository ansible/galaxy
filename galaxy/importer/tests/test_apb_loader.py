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
import yaml
import pytest

from galaxy import constants
from galaxy.importer import exceptions as exc
from galaxy.importer import loaders
from galaxy.importer.loaders import apb as apb_loader

APB_DATA = """
version: '1.0.0'
name: mssql-apb
description: Deployment of Microsoft SQL Server on Linux
bindable: true
async: optional
metadata:
  displayName: Microsoft SQL Server on Linux
  imageUrl:
    'https://raw.githubusercontent.com/ansibleplaybookbundle/mssql-apb/master/docs/img/sql-server.png'
  documentationUrl:
    'https://docs.microsoft.com/en-us/sql/linux/sql-server-linux-overview'
  dependencies: ['registry.centos.org/microsoft/mssql-server-linux']
tags:
  - database
  - mssql
plans:
  - name: ephemeral
    description: This plan deploys an ephemeral Microsoft SQL Server on Linux
    free: true
    default: true
    metadata:
      displayName: Ephemeral installation
      longDescription:
        This plan will deploy a standalone Microsoft SQL Server on Linux
        using ephemeral storage
    parameters:
      - name: ACCEPT_EULA
        title: Accept the End-User Licensing Agreement
        type: boolean
        required: true
        default: false
        description: http://go.microsoft.com/fwlink/?LinkId=746388
        display_group: EULA Required
      - name: MSSQL_PASSWORD
        required: true
        default: "Hello123!"
        type: string
        display_type: password
        title: "Database Admin (SA) Password"
        description:
          "The password must be at least 8 characters long and contain
          characters from three of the following four sets: Uppercase
          letters, Lowercase letters, Base 10 digits, and Symbols"
        display_group: Microsoft SQL Config
        min_length: 8
        max_length: 128
      - name: MSSQL_DATABASE
        required: true
        default: TestDB
        pattern: "^[a-zA-Z0-9_-]*$"
        type: string
        title: Microsoft SQL Database Name
        display_group: Microsoft SQL Config
      - name: MSSQL_AGENT_ENABLED
        title: Enable SQL Server Agent
        type: boolean
        required: true
        default: false
        display_group: Microsoft SQL Config
      - name: MSSQL_PID
        required: true
        type: enum
        enum: ['Developer', 'Evaluation']
        default: Developer
        title: SQL Server Edition
        display_group: Microsoft SQL Config
      - name: MSSQL_LOCAL_IS
        title: Use existing mssql-server-linux imagestream in project
        type: boolean
        required: true
        default: false
        display_group: Microsoft SQL Config
      - name: MSSQL_LCID
        title: Language ID
        type: integer
        required: true
        default: 1033
        description: e.g., 1033 is English (US), 1036 is French
        min_length: 4
        max_length: 4
        display_group: Microsoft SQL Config
      - name: MSSQL_IMAGE_PULL
        title: "DeploymentConfig Image pull policy"
        type: enum
        enum: ['Always', 'IfNotPresent', 'Never']
        required: true
        default: IfNotPresent
        display_group: Microsoft SQL Config
      - name: MSSQL_MEMORY_LIMIT
        required: true
        default: 3
        type: integer
        title:
          Maximum amount of memory the container can use (in GB) eg 1GB 2GB
        display_group: Environment Sizing
      - name: MSSQL_MEMORY_REQUEST
        required: true
        default: 2
        type: integer
        title:
          Requested amount of memory for the container to start (in GB)
          eg 1GB 2GB
        display_group: Environment Sizing

  - name: persistent
    description: This plan deploys a persistent Microsoft SQL Server on Linux
    free: true
    metadata:
      displayName: Persistent installation
      longDescription:
        This plan will deploy a standalone Microsoft SQL Server on Linux
        using persistent storage
    parameters:
      - name: ACCEPT_EULA
        title: Accept the End-User Licensing Agreement
        type: boolean
        required: true
        default: false
        description: http://go.microsoft.com/fwlink/?LinkId=746388
        display_group: EULA Required
      - name: MSSQL_PASSWORD
        required: true
        default: "Hello123!"
        type: string
        display_type: password
        title: "Database Admin (SA) Password"
        description:
          "The password must be at least 8 characters long and contain
          characters from three of the following four sets: Uppercase
          letters, Lowercase letters, Base 10 digits, and Symbols"
        display_group: Microsoft SQL Config
        min_length: 8
        max_length: 128
      - name: MSSQL_DATABASE
        required: true
        default: TestDB
        pattern: "^[a-zA-Z0-9_-]*$"
        type: string
        title: Microsoft SQL Database Name
        display_group: Microsoft SQL Config
      - name: MSSQL_AGENT_ENABLED
        title: Enable SQL Server Agent
        type: boolean
        required: true
        default: false
        display_group: Microsoft SQL Config
      - name: MSSQL_PID
        required: true
        type: enum
        enum: ['Developer', 'Evaluation']
        default: Developer
        title: SQL Server Edition
        display_group: Microsoft SQL Config
      - name: MSSQL_LOCAL_IS
        title: Use existing mssql-server-linux imagestream in project
        type: boolean
        required: true
        default: false
        display_group: Microsoft SQL Config
      - name: MSSQL_LCID
        title: Language ID
        type: integer
        required: true
        default: 1033
        description: e.g., 1033 is English (US), 1036 is French
        min_length: 4
        max_length: 4
        display_group: Microsoft SQL Config
      - name: MSSQL_IMAGE_PULL
        title: "DeploymentConfig Image pull policy"
        type: enum
        enum: ['Always', 'IfNotPresent', 'Never']
        required: true
        default: IfNotPresent
        display_group: Microsoft SQL Config
      - name: MSSQL_DATA_STORAGE_SIZE
        required: true
        default: 1
        type: integer
        title: Persistent volume size for db data (in GB) eg 1GB 2GB
        display_group: Environment Sizing
      - name: MSSQL_MEMORY_LIMIT
        required: true
        default: 3
        type: integer
        title:
          Maximum amount of memory the container can use (in GB) eg 1GB 2GB
        display_group: Environment Sizing
      - name: MSSQL_MEMORY_REQUEST
        required: true
        default: 2
        type: integer
        title:
          Requested amount of memory for the container to start (in GB)
          eg 1GB 2GB
        display_group: Environment Sizing
"""


class TestAPBMetaParser(unittest.TestCase):

    def setUp(self):
        log_mock = mock.patch('galaxy.importer.loaders.base.default_logger')
        self.log = log_mock.start()
        self.addCleanup(log_mock.stop)
        self.data = yaml.load(APB_DATA)

    def test_parse_tags(self):
        parser = apb_loader.APBMetaParser(self.data, self.log)
        tags = parser.parse_tags()
        assert tags == ['database', 'mssql']

    def test_invalid_tags(self):
        self.data['tags'] = ['database', 'MSSQL', 'mssql-', 'mssql_',
                             'postgres1']
        parser = apb_loader.APBMetaParser(self.data, self.log)
        tags = parser.parse_tags()
        assert tags == ['database', 'postgres1']

    def test_parse_name(self):
        parser = apb_loader.APBMetaParser(self.data, self.log)
        name = parser.parse_name()
        assert name == 'mssql_apb'

    def test_parse_description(self):
        parser = apb_loader.APBMetaParser(self.data, self.log)
        descr = parser.parse_description()
        assert descr == 'Deployment of Microsoft SQL Server on Linux'

    def test_invalid_metadata(self):
        self.data['metadata'] = ''
        parser = apb_loader.APBMetaParser(self.data, self.log)
        with pytest.raises(exc.APBContentLoadError) as excinfo:
            parser.check_data()
        msg = 'Expecting "metadata" in metadata to be a dictionary'
        assert msg in excinfo.value.message

    def test_invalid_bindable(self):
        self.data['bindable'] = 'foo'
        parser = apb_loader.APBMetaParser(self.data, self.log)
        with pytest.raises(exc.APBContentLoadError) as excinfo:
            parser.check_data()
        msg = 'Expecting "bindable" in metadata to be a boolean'
        assert msg in excinfo.value.message

    def test_invalid_plans(self):
        self.data['plans'] = 'foo'
        parser = apb_loader.APBMetaParser(self.data, self.log)
        with pytest.raises(exc.APBContentLoadError) as excinfo:
            parser.check_data()
        msg = 'Expecting "plans" in metadata to be a list'
        assert msg in excinfo.value.message

    def test_invalid_plan_name(self):
        del self.data['plans'][0]['name']
        parser = apb_loader.APBMetaParser(self.data, self.log)
        with pytest.raises(exc.APBContentLoadError) as excinfo:
            parser.check_data()
        msg = 'Expecting "name" to be defined for each plan'
        assert msg in excinfo.value.message

    def test_plan_parameters_type(self):
        self.data['plans'][0]['parameters'] = 'foo'
        parser = apb_loader.APBMetaParser(self.data, self.log)
        with pytest.raises(exc.APBContentLoadError) as excinfo:
            parser.check_data()
        msg = 'Expecting "parameters" in "plans[0]" of'
        assert msg in excinfo.value.message

    def test_plan_parameters_item_type(self):
        self.data['plans'][0]['parameters'] = ['foo']
        parser = apb_loader.APBMetaParser(self.data, self.log)
        with pytest.raises(exc.APBContentLoadError) as excinfo:
            parser.check_data()
        msg = 'Expecting "parameters[0]" in "plans[0]" of'
        assert msg in excinfo.value.message

    def test_missing_async(self):
        del self.data['async']
        parser = apb_loader.APBMetaParser(self.data, self.log)
        with pytest.raises(exc.APBContentLoadError) as excinfo:
            parser.check_data()
        msg = 'Missing "async" field in metadata.'
        assert msg in excinfo.value.message

    def test_async_bad_value(self):
        self.data['async'] = 'foo'
        parser = apb_loader.APBMetaParser(self.data, self.log)
        with pytest.raises(exc.APBContentLoadError) as excinfo:
            parser.check_data()
        msg = 'Expecting "async" in metadata to be one of'
        assert msg in excinfo.value.message

    def test_missing_version(self):
        del self.data['version']
        parser = apb_loader.APBMetaParser(self.data, self.log)
        with pytest.raises(exc.APBContentLoadError) as excinfo:
            parser.check_data()
        msg = 'Missing "version" field in metadata.'
        assert msg in excinfo.value.message

    def test_param_keys(self):
        parser = apb_loader.APBMetaParser(self.data, self.log)
        parser.check_data()
        metadata = parser.parse_metadata()
        assert 'displayGroup' in metadata['plans'][0]['parameters'][0]
        assert 'displayType' in metadata['plans'][0]['parameters'][1]
        assert 'displayGroup' in metadata['plans'][0]['parameters'][1]
        assert 'minLength' in metadata['plans'][0]['parameters'][1]
        assert 'maxLength' in metadata['plans'][0]['parameters'][1]

    def test_version_format(self):
        self.data['version'] = 'foo'
        parser = apb_loader.APBMetaParser(self.data, self.log)
        parser._check_version()
        self.log.warning.assert_called_once_with(
            'Version "foo" in metadata does not match the expected version '
            'format')

    def test_invalid_version(self):
        self.data['version'] = 1.1
        parser = apb_loader.APBMetaParser(self.data, self.log)
        parser._check_version()
        self.log.warning.assert_called_once_with(
            'Version value in metadata is not a string')


class TestRoleLoader(unittest.TestCase):
    @mock.patch.object(loaders.APBLoader, '_load_metadata')
    def test_load_role(self, load_metadata_mock):
        load_metadata_mock.return_value = (yaml.load(APB_DATA))
        loader = loaders.APBLoader(
            constants.ContentType.APB, 'apbs/test_apb', '/tmp/repo',
            metadata_path='apb.yaml')
        apb = loader.load()
        role_meta = apb.role_meta
        metadata = apb.metadata['apb_metadata']

        assert apb.name == 'mssql_apb'
        assert len(metadata['metadata']['dependencies']) == 1
        assert apb.description == 'Deployment of Microsoft SQL Server on Linux'
        assert role_meta['tags'] == ['database', 'mssql']
