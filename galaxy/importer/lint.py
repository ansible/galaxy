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

import subprocess

import six


class BaseLinter(object):

    def check_files(self, paths):
        pass


class Flake8Linter(BaseLinter):

    cmd = 'flake8'

    def __init__(self, workdir=None):
        self.workdir = workdir

    def check_files(self, paths):
        if isinstance(paths, six.string_types):
            paths = [paths]

        cmd = [self.cmd, '--exit-zero', '--isolated', '--'] + paths
        proc = subprocess.Popen(cmd, cwd=self.workdir, stdout=subprocess.PIPE)
        for line in proc.stdout:
            yield line.strip()
        proc.wait()


class YamlLinter(BaseLinter):

    cmd = 'yamllint'

    def __init__(self, workdir=None):
        self.workdir = workdir

    def check_files(self, paths):
        if isinstance(paths, six.string_types):
            paths = [paths]

        cmd = [self.cmd, '-f', 'parsable', '--'] + paths
        proc = subprocess.Popen(cmd, cwd=self.workdir, stdout=subprocess.PIPE)
        for line in proc.stdout:
            yield line.strip()
        proc.wait()
