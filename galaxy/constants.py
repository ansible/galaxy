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
import logging
import re


MAX_TAGS_COUNT = 20
PROVIDER_GITHUB = 'GitHub'
TAG_REGEXP = re.compile('^[a-z0-9]+$')


class Enum(enum.Enum):
    """
    Values stored as `value`, `description` tuples to be used as `choices`
    parameter for Django string fields.
    """

    @classmethod
    def choices(cls):
        return [(x.value, x.value) for x in cls]

    def __str__(self):
        return self.value


class RoleType(Enum):
    ANSIBLE = 'ANS'
    CONTAINER = 'CON'
    CONTAINER_APP = 'APP'
    DEMO = 'DEM'

    @classmethod
    def choices(cls):
        return [
            (cls.ANSIBLE.value, 'Ansible'),
            (cls.CONTAINER.value, 'Container Enabled'),
            (cls.CONTAINER_APP.value, 'Container App'),
            (cls.DEMO.value, 'Demo')
        ]


class ContentType(Enum):
    # FIXME(cutwater): Add module_utils type
    APB = 'apb'
    ROLE = 'role'
    MODULE = 'module'
    MODULE_UTILS = 'module_utils'
    ACTION_PLUGIN = 'action_plugin'
    CACHE_PLUGIN = 'cache_plugin'
    CALLBACK_PLUGIN = 'callback_plugin'
    CLICONF_PLUGIN = 'cliconf_plugin'
    CONNECTION_PLUGIN = 'connection_plugin'
    FILTER_PLUGIN = 'filter_plugin'
    INVENTORY_PLUGIN = 'inventory_plugin'
    LOOKUP_PLUGIN = 'lookup_plugin'
    NETCONF_PLUGIN = 'netconf_plugin'
    SHELL_PLUGIN = 'shell_plugin'
    STRATEGY_PLUGIN = 'strategy_plugin'
    TERMINAL_PLUGIN = 'terminal_plugin'
    TEST_PLUGIN = 'test_plugin'

    @classmethod
    def choices(cls):
        return [
            (cls.APB.value, 'Ansible Playbook Bundle'),
            (cls.ROLE.value, 'Role'),
            (cls.MODULE.value, 'Module'),
            (cls.MODULE_UTILS.value, 'Module Utils'),
            (cls.ACTION_PLUGIN.value, 'Action Plugin'),
            (cls.CACHE_PLUGIN.value, 'Cache Plugin'),
            (cls.CALLBACK_PLUGIN.value, 'Callback Plugin'),
            (cls.CLICONF_PLUGIN.value, 'CLI Conf Plugin'),
            (cls.CONNECTION_PLUGIN.value, 'Connection Plugin'),
            (cls.FILTER_PLUGIN.value, 'Filter Plugin'),
            (cls.INVENTORY_PLUGIN.value, 'Inventory Plugin'),
            (cls.LOOKUP_PLUGIN.value, 'Lookup Plugin'),
            (cls.NETCONF_PLUGIN.value, 'Netconf Plugin'),
            (cls.SHELL_PLUGIN.value, 'Shell Plugin'),
            (cls.STRATEGY_PLUGIN.value, 'Strategy Plugin'),
            (cls.TERMINAL_PLUGIN.value, 'Terminal Plugin'),
            (cls.TEST_PLUGIN.value, 'Test Plugin'),
        ]


class ImportTaskMessageType(Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    SUCCESS = 'SUCCESS'
    # FIXME(cutwater): ERROR and FAILED types seem to be redundant
    FAILED = 'FAILED'
    ERROR = 'ERROR'

    @classmethod
    def from_logging_level(cls, level):
        if level == logging.INFO:
            return cls.INFO
        elif level == logging.WARNING:
            return cls.WARNING
        elif level == logging.ERROR:
            return cls.ERROR
        else:
            # Note(cutwater): Fallback to DEBUG level
            return cls.DEBUG


class ImportTaskState(Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
