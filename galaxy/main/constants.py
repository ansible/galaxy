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

from __future__ import unicode_literals

import enum


class DjangoEnum(enum.Enum):
    """
    Values stored as `value`, `description` tuples to be used as `choices`
    parameter for Django string fields.
    """

    @property
    def value(self):
        return self._value_[0]

    @classmethod
    def choices(cls):
        return [item._value_ for item in cls]


class RoleType(DjangoEnum):
    ANSIBLE = ('ANS', 'Ansible')
    CONTAINER = ('CON', 'Container Enabled')
    CONTAINER_APP = ('APP', 'Container App')
    DEMO = ('DEM', 'Demo')


class ContentType(DjangoEnum):
    ROLE = ('role', 'Role')
    MODULE = ('module', 'Module')
    ACTION_PLUGIN = ('action_plugin', 'Action Plugin')
    CACHE_PLUGIN = ('cache_plugin', 'Cache Plugin')
    CALLBACK_PLUGIN = ('callback_plugin', 'Callback Plugin')
    CLICONF_PLUGIN = ('cliconf_plugin', 'CLI Conf Plugin')
    CONNECTION_PLUGIN = ('connection_plugin', 'Connection Plugin')
    FILTER_PLUGIN = ('filter_plugin', 'Filter Plugin')
    INVENTORY_PLUGIN = ('inventory_plugin', 'Inventory Plugin')
    LOOKUP_PLUGIN = ('lookup_plugin', 'Lookup Plugin')
    NETCONF_PLUGIN = ('netconf_plugin', 'Netconf Plugin')
    SHELL_PLUGIN = ('shell_plugin', 'Shell Plugin')
    STRATEGY_PLUGIN = ('strategy_plugin', 'Strategy Plugin')
    TERMINAL_PLUGIN = ('terminal_plugin', 'Terminal Plugin')
    TEST_PLUGIN = ('test_plugin', 'Test Plugin')


class ImportTaskMessageType(DjangoEnum):
    INFO = ('INFO', 'INFO')
    WARNING = ('WARNING', 'WARNING')
    SUCCESS = ('SUCEESS', 'SUCCESS')
    # FIXME(cutwater): ERROR and FAILED types seem to be redundant
    FAILED = ('FAILED', 'FAILED')
    ERROR = ('ERROR', 'ERROR')


class ImportTaskState(DjangoEnum):
    PENDING = ('PENDING', 'PENDING')
    RUNNING = ('RUNNING', 'RUNNING')
    FAILED = ('FAILED', 'FAILED')
    SUCCESS = ('SUCCESS', 'SUCCESS')
