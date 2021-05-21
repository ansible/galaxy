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

import tempfile
import os
import shutil
import pytest

from galaxy.importer import linters


FLAKE8_TEST_FILE_OK = """
x = 1
y = 2
if x == 3 or y == 4:
    pass
"""


def test_flake8_ok():
    with tempfile.NamedTemporaryFile('w') as fp:
        fp.write(FLAKE8_TEST_FILE_OK)
        fp.flush()

        linter = linters.Flake8Linter()
        result = list(linter.check_files(fp.name))
    assert result == []


FLAKE8_TEST_FILE_FAIL = """
if (
        x == (
            3
        ) or
        y == 4):
\tpass
"""


def test_flake8_fail():
    with tempfile.NamedTemporaryFile('w') as fp:
        fp.write(FLAKE8_TEST_FILE_FAIL)
        fp.flush()

        linter = linters.Flake8Linter()
        result = list(linter.check_files(fp.name))

        expected = [
            "{0}:3:9: F821 undefined name 'x'",
            "{0}:6:9: F821 undefined name 'y'",
            "{0}:7:1: E101 indentation contains mixed spaces and tabs",
            "{0}:7:1: W191 indentation contains tabs",
            "{0}:7:2: E117 over-indented",
        ]
        expected = [s.format(fp.name) for s in expected]
    assert sorted(result) == sorted(expected)


YAMLLINT_TEST_FILE_OK = """---
x:
  - y
  - z
"""


def test_yamllint_ok():
    with tempfile.NamedTemporaryFile('w') as fp:
        fp.write(YAMLLINT_TEST_FILE_OK)
        fp.flush()

        linter = linters.YamlLinter()
        result = list(linter.check_files(fp.name))
    assert result == []


YAMLLINT_TEST_FILE_FAIL = """
x:
  - y
  -    z
"""


def test_yamllint_fail():
    with tempfile.NamedTemporaryFile('w') as fp:
        fp.write(YAMLLINT_TEST_FILE_FAIL)
        fp.flush()

        linter = linters.YamlLinter()
        result = list(linter.check_files(fp.name))

        expected = [
            '{0}:1:1: [error] too many blank lines (1 > 0) (empty-lines)',
            '{0}:4:7: [error] too many spaces after hyphen (hyphens)',
        ]
        expected = [s.format(fp.name) for s in expected]
    assert sorted(result) == sorted(expected)


ANSIBLELINT_ROLEPATH = 'role/tasks'


def get_ansiblelint_filename(root):
    full_path = os.path.join(root, ANSIBLELINT_ROLEPATH)
    os.makedirs(full_path)
    return os.path.join(full_path, 'main.yml')


def get_ansiblelint_root(root):
    return '/'.join((root, ANSIBLELINT_ROLEPATH.split('/')[0]))


@pytest.fixture
def temp_root():
    try:
        tmp = tempfile.mkdtemp()
        yield tmp
    finally:
        shutil.rmtree(tmp)


ANSIBLELINT_TEST_FILE_OK = """---
- name: Add mongodb repo apt_key
  become: true
  apt_key: keyserver=hkp
  until: result.rc == 0
"""


def test_ansiblelint_ok(temp_root):
    with open(get_ansiblelint_filename(temp_root), 'w') as fp:
        fp.write(ANSIBLELINT_TEST_FILE_OK)
        fp.flush()

        linter = linters.AnsibleLinter()
        linter.root = get_ansiblelint_root(temp_root)
        result = list(linter.check_files(['.']))
    assert result == []


ANSIBLELINT_TASK_WARN = """---
- name: edit vimrc
  lineinfile:
    path: /etc/vimrc
    line: "{{var_spacing_problem}}"
"""


def test_ansiblelint_fail(temp_root):
    with open(get_ansiblelint_filename(temp_root), 'w') as fp:
        fp.write(ANSIBLELINT_TASK_WARN)
        fp.flush()

        linter = linters.AnsibleLinter()
        linter.root = get_ansiblelint_root(temp_root)
        result = list(linter.check_files(['.']))
        expected = 'variables should have spaces before and after'
    assert expected in ' '.join(result).lower()


ANSIBLELINT_TEST_FILE_FAIL_APP = """---
- name: Copy local file to remote
  sudo: true
  copy:
    src: vars.yml
    dest: {{ dest_proj_path }}/config/ansible/vars.yml
"""


def test_ansiblelint_fail_app(temp_root):
    with open(get_ansiblelint_filename(temp_root), 'w') as fp:
        fp.write(ANSIBLELINT_TEST_FILE_FAIL_APP)
        fp.flush()

        linter = linters.AnsibleLinter()
        linter.root = get_ansiblelint_root(temp_root)
        result = list(linter.check_files(['.']))
        expected = 'exception running ansible-lint'
    assert expected in ' '.join(result).lower()
