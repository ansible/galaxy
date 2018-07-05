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

import six


logger = logging.getLogger(__name__)

LINTERS_DIR = os.path.abspath(os.path.dirname(__file__))
FLAKE8_MAX_LINE_LENGTH = 120
FLAKE8_IGNORE_ERRORS = 'E402'


class BaseLinter(object):

    def __init__(self, workdir=None):
        self.root = workdir

    def check_files(self, paths):
        if isinstance(paths, six.string_types):
            paths = [paths]
        paths = map(os.path.normpath, paths)
        return self._check_files(paths)

    def _check_files(self, paths):
        pass


class Flake8Linter(BaseLinter):

    cmd = 'flake8'

    def _check_files(self, paths):
        cmd = [self.cmd, '--exit-zero', '--isolated',
               '--ignore', FLAKE8_IGNORE_ERRORS,
               '--max-line-length', str(FLAKE8_MAX_LINE_LENGTH),
               '--'] + paths
        logger.info('CMD: ' + ' '.join(cmd))
        proc = subprocess.Popen(cmd, cwd=self.root, stdout=subprocess.PIPE)
        for line in proc.stdout:
            yield line.strip()
        proc.wait()


class YamlLinter(BaseLinter):

    cmd = 'yamllint'
    config = os.path.join(LINTERS_DIR, 'yamllint.yaml')

    def _check_files(self, paths):
        cmd = [self.cmd, '-f', 'parsable', '-c', self.config, '--'] + paths
        logger.info('CMD: ' + ' '.join(cmd))
        proc = subprocess.Popen(cmd, cwd=self.root, stdout=subprocess.PIPE)
        for line in proc.stdout:
            yield line.strip()
        proc.wait()


class AnsibleReviewLinter(BaseLinter):

    exclude_file = config = os.path.join(LINTERS_DIR, 'git-exclude.txt')
    config = os.path.join(LINTERS_DIR, 'ansible-review.cfg')
    ignore = os.path.join(LINTERS_DIR, 'ignore-files')

    def _check_files(self, paths):
        cmd = ['find', '.', '-type', 'f']
        cmd += self._get_exclustions()
        logger.info('CMD: ' + ' '.join(cmd))
        proc = subprocess.Popen(cmd, cwd=self.root, stdout=subprocess.PIPE)
        cmd2 = ['xargs', '/var/lib/galaxy/venv/bin/ansible-review', '-c',
                self.config, '-f', 'json']
        proc2 = subprocess.Popen(cmd2, cwd=self.root, stdout=subprocess.PIPE, stdin=proc.stdout,
                                 stderr=subprocess.STDOUT)
        for line in proc2.stdout:
            yield line.strip()
        proc.wait()

    def _get_exclustions(self):
        cmd = []
        with open(self.ignore, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if not line.startswith('#'):
                line_type = 'path' if '/' in line else 'name'
                cmd += ['-not', '-%s' % line_type, line.rstrip('\n')]
        return cmd
