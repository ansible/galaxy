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

import os
import subprocess
import logging


logger = logging.getLogger(__name__)

LINTERS_DIR = os.path.abspath(os.path.dirname(__file__))
FLAKE8_MAX_LINE_LENGTH = 120
FLAKE8_IGNORE_ERRORS = 'E402'
FLAKE8_SELECT_ERRORS = 'E,F,W'


class BaseLinter(object):

    def __init__(self, workdir=None):
        self.root = workdir

    def check_files(self, paths):
        if isinstance(paths, str):
            paths = [paths]
        paths = [os.path.normpath(p) for p in paths]
        return self._check_files(paths)

    def _check_files(self, paths):
        pass


class Flake8Linter(BaseLinter):

    id = 'flake8'
    cmd = 'flake8'

    def _check_files(self, paths):
        cmd = [self.cmd, '--exit-zero', '--isolated',
               '--ignore', FLAKE8_IGNORE_ERRORS,
               '--select', FLAKE8_SELECT_ERRORS,
               '--max-line-length', str(FLAKE8_MAX_LINE_LENGTH),
               '--'] + paths
        logger.debug('CMD: ' + ' '.join(cmd))
        proc = subprocess.Popen(cmd, cwd=self.root, stdout=subprocess.PIPE)
        for line in proc.stdout:
            # TODO(cutwater): Replace `.decode('utf-8')` call with subprocess
            # parameter `encoding` after dropping Python 2.7 support.
            yield line.decode('utf-8').strip()
        proc.wait()

    def parse_id_and_desc(self, message):
        try:
            msg_parts = message.split(' ')
            rule_desc = ' '.join(msg_parts[2:])

            error_id = msg_parts[1]
            # REVIEW(cutwater): Flake8 is configured to return `E,F,W` rules.
            #   Why is parsing rules prefixes list differs
            #   from FLAKE8_SELECT_ERRORS.
            if error_id[0] not in ['E', 'W']:
                error_id = None

        except IndexError:
            # REVIEW(cutwater): If this except clause is executed,
            #  rule_desc may not be defined, but it's used below.
            error_id = None

        if not error_id:
            # REVIEW(cutwater): Couple of questions here:
            #   1. Why is that error?
            #   2. Why displaying command that was executed
            #      but not the message that is parsed?
            logger.error('No error_id found in message: {}'.format(self.cmd))
            return None, None

        # REVIEW(cutwater): rule_desc reference can be undefined here.
        return error_id, rule_desc


class YamlLinter(BaseLinter):

    id = 'yamllint'
    cmd = 'yamllint'
    config = os.path.join(LINTERS_DIR, 'yamllint.yaml')

    def _check_files(self, paths):
        cmd = [self.cmd, '-f', 'parsable', '-c', self.config, '--'] + paths
        logger.debug('CMD: ' + ' '.join(cmd))
        proc = subprocess.Popen(cmd, cwd=self.root, stdout=subprocess.PIPE)
        for line in proc.stdout:
            # TODO(cutwater): Replace `.decode('utf-8')` call with subprocess
            # parameter `encoding` after dropping Python 2.7 support.
            yield line.decode('utf-8').strip()
        proc.wait()

    def parse_id_and_desc(self, message):
        try:
            msg_parts = message.split(' ')
            rule_desc = ' '.join(msg_parts[2:])

            error_id = 'YAML_{}'.format(msg_parts[1][1:-1]).upper()
            if error_id not in ['YAML_ERROR', 'YAML_WARNING']:
                error_id = None

        except IndexError:
            error_id = None

        if not error_id:
            logger.error('No error_id found in {} message'.format(self.cmd))
            return None, None

        return error_id, rule_desc


class AnsibleLinter(BaseLinter):

    id = 'ansible-lint'
    cmd = 'ansible-lint'

    def _check_files(self, paths):
        cmd = [self.cmd, '-p'] + paths
        logger.debug('CMD: ' + ' '.join(cmd))
        proc = subprocess.Popen(cmd, cwd=self.root, stdout=subprocess.PIPE)

        for line in proc.stdout:
            # TODO(cutwater): Replace `.decode('utf-8')` call with subprocess
            # parameter `encoding` after dropping Python 2.7 support.
            line_list = line.decode('utf-8').split(' ')
            rel_path = ['.'] + line_list[0].split('/')[3:]
            line_list[0] = '/'.join(rel_path)
            line = ' '.join(line_list)
            yield line.strip()

        # returncode 1 is app exception, 0 is no linter err, 2 is linter err
        if proc.wait() not in (0, 2):
            yield 'Exception running ansible-lint, could not complete linting'

    def parse_id_and_desc(self, message):
        try:
            msg_parts = message.split(' ')
            rule_desc = ' '.join(msg_parts[2:])

            error_id = msg_parts[1][1:-1]
            if error_id[0] not in ['E']:
                error_id = None

        except IndexError:
            error_id = None

        if not error_id:
            logger.error('No error_id found in {} message'.format(self.cmd))
            return None, None

        return error_id, rule_desc
