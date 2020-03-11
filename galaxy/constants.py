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

import enum
import logging
import re

from pulpcore import constants as pulp_const


MAX_TAGS_COUNT = 20
MAX_UPLOAD_FILE_SIZE_BYTES = 20 * 1000 * 1000  # 20MB
PROVIDER_GITHUB = 'GitHub'
ROLE_TAG_REGEXP = re.compile(r'^[a-z0-9]+$')
NAME_REGEXP = re.compile(r'^(?!.*__)[a-z]+[0-9a-z_]*$')
CONTENT_NAME_REGEXP = re.compile(r'^(?!.*__)[a-z_]+[0-9a-z_]*$')
MATCH_LEADING_NUMBER_REGEXP = re.compile(r'^[0-9]')


NS_TYPE_COMMUNITY = 'community'
NS_TYPE_PARTNER = 'partner'
NS_TYPES = [
    NS_TYPE_COMMUNITY,
    NS_TYPE_PARTNER,
]


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
    APB = 'apb'
    ROLE = 'role'
    MODULE = 'module'
    MODULE_UTILS = 'module_utils'
    ACTION_PLUGIN = 'action'
    BECOME_PLUGIN = 'become'
    CACHE_PLUGIN = 'cache'
    CALLBACK_PLUGIN = 'callback'
    CLICONF_PLUGIN = 'cliconf'
    CONNECTION_PLUGIN = 'connection'
    DOC_FRAGMENTS_PLUGIN = 'doc_fragments'
    FILTER_PLUGIN = 'filter'
    HTTPAPI_PLUGIN = 'httpapi'
    INVENTORY_PLUGIN = 'inventory'
    LOOKUP_PLUGIN = 'lookup'
    NETCONF_PLUGIN = 'netconf'
    SHELL_PLUGIN = 'shell'
    STRATEGY_PLUGIN = 'strategy'
    TERMINAL_PLUGIN = 'terminal'
    TEST_PLUGIN = 'test'
    VARS_PLUGIN = 'vars'

    @classmethod
    def choices(cls):
        return [
            (cls.APB.value, 'Ansible Playbook Bundle'),
            (cls.ROLE.value, 'Role'),
            (cls.MODULE.value, 'Module'),
            (cls.MODULE_UTILS.value, 'Module Utils'),
            (cls.ACTION_PLUGIN.value, 'Action Plugin'),
            (cls.BECOME_PLUGIN.value, 'Become Plugin'),
            (cls.CACHE_PLUGIN.value, 'Cache Plugin'),
            (cls.CALLBACK_PLUGIN.value, 'Callback Plugin'),
            (cls.CLICONF_PLUGIN.value, 'CLI Conf Plugin'),
            (cls.CONNECTION_PLUGIN.value, 'Connection Plugin'),
            (cls.DOC_FRAGMENTS_PLUGIN.value, 'Doc Fragments Plugin'),
            (cls.FILTER_PLUGIN.value, 'Filter Plugin'),
            (cls.HTTPAPI_PLUGIN.value, 'HTTP API Plugin'),
            (cls.INVENTORY_PLUGIN.value, 'Inventory Plugin'),
            (cls.LOOKUP_PLUGIN.value, 'Lookup Plugin'),
            (cls.NETCONF_PLUGIN.value, 'Netconf Plugin'),
            (cls.SHELL_PLUGIN.value, 'Shell Plugin'),
            (cls.STRATEGY_PLUGIN.value, 'Strategy Plugin'),
            (cls.TERMINAL_PLUGIN.value, 'Terminal Plugin'),
            (cls.TEST_PLUGIN.value, 'Test Plugin'),
            (cls.VARS_PLUGIN.value, 'Vars Plugin'),
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

    def as_task_state(self):
        if self is self.PENDING:
            return pulp_const.TASK_STATES.WAITING
        elif self is self.RUNNING:
            return pulp_const.TASK_STATES.RUNNING
        elif self is self.FAILED:
            return pulp_const.TASK_STATES.FAILED
        elif self is self.SUCCESS:
            return pulp_const.TASK_STATES.COMPLETED


class LinterType(Enum):
    FLAKE8 = 'flake8'
    YAMLLINT = 'yamllint'
    ANSIBLELINT = 'ansible-lint'

    @classmethod
    def choices(cls):
        return [
            (cls.FLAKE8.value, 'flake8'),
            (cls.YAMLLINT.value, 'yamllint'),
            (cls.ANSIBLELINT.value, 'ansible-lint')
        ]


class RepositoryFormat(enum.Enum):
    ROLE = 'role'
    APB = 'apb'
    MULTI = 'multi'

    @classmethod
    def choices(cls):
        return [
            (cls.ROLE.value, 'Role'),
            (cls.APB.value, 'Ansible Playbook Bundle'),
            (cls.MULTI.value, 'Multi-content'),
        ]
