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

        result = []
        error_ids = []
        descriptions = []
        for message in linter.check_files(fp.name):
            result.append(message)
            error_id, rule_desc = linter.parse_id_and_desc(message)
            error_ids.append(error_id)
            descriptions.append(rule_desc)

        expected = [
            "{0}:3:9: F821 undefined name 'x'",
            "{0}:5:11: W504 line break after binary operator",
            "{0}:6:9: F821 undefined name 'y'",
            "{0}:7:1: E101 indentation contains mixed spaces and tabs",
            "{0}:7:1: W191 indentation contains tabs",
            "{0}:7:2: E117 over-indented",
        ]
        expected = [s.format(fp.name) for s in expected]
    assert sorted(result) == sorted(expected)
    assert 'W504' in error_ids
    assert 'E117' in error_ids
    assert 'F821' in error_ids
    assert 'undefined name' in ' '.join(descriptions).lower()
    assert 'over-indented' in ' '.join(descriptions).lower()


def test_flake8_error_id_match():
    linter = linters.Flake8Linter()
    msg_e501 = 'file.py:99:80: E501 line too long (81 > 79 characters)'
    msg_f401 = 'forms.py:5:1: F401 "pyaml" imported but unused'
    msg_w191 = 'plugin.py:7:2: W191 indentation contains tabs'

    error_id, _ = linter.parse_id_and_desc(msg_e501)
    assert error_id == 'E501'

    error_id, _ = linter.parse_id_and_desc(msg_f401)
    assert error_id == 'F401'

    error_id, _ = linter.parse_id_and_desc(msg_w191)
    assert error_id == 'W191'


def test_flake8_error_id_not_match():
    linter = linters.Flake8Linter()
    messages = [
        'file.py:99:80: C901 mccabe plugin',
        'forms.py:5:1: N801 naming convention',
        '',
        'plugin.py:7:2: [E301] brackets',
        'E501 line too long (81 > 79 characters)',
    ]

    for msg in messages:
        error_id, _ = linter.parse_id_and_desc(msg)
        assert error_id is None


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

        result = []
        error_ids = []
        descriptions = []
        for message in linter.check_files(fp.name):
            result.append(message)
            error_id, rule_desc = linter.parse_id_and_desc(message)
            error_ids.append(error_id)
            descriptions.append(rule_desc)

        expected = [
            '{0}:1:1: [error] too many blank lines (1 > 0) (empty-lines)',
            '{0}:4:7: [error] too many spaces after hyphen (hyphens)',
        ]
        expected = [s.format(fp.name) for s in expected]
    assert sorted(result) == sorted(expected)
    assert 'YAML_ERROR' in error_ids
    assert 'too many spaces after hyphen' in ' '.join(descriptions).lower()


ANSIBLELINT_TEST_FILE_OK = """
---
- name: Test playbook
  tasks:
  - name: Add mongodb repo apt_key
    become: true
    apt_key: keyserver=hkp
    until: result.rc == 0
"""


def test_ansiblelint_ok():
    with tempfile.NamedTemporaryFile('w', suffix='.yaml') as fp:
        fp.write(ANSIBLELINT_TEST_FILE_OK)
        fp.flush()

        linter = linters.AnsibleLinter()
        result = list(linter.check_files(fp.name))
    assert result == []


ANSIBLELINT_TEST_FILE_FAIL = """
---
- name: Test playbook
  tasks:
  - name: edit vimrc
    sudo: true
    lineinfile:
      path: /etc/vimrc
      line: '# added via ansible'
"""


def test_ansiblelint_fail():
    with tempfile.NamedTemporaryFile('w', suffix='.yaml') as fp:
        fp.write(ANSIBLELINT_TEST_FILE_FAIL)
        fp.flush()

        linter = linters.AnsibleLinter()

        error_ids = []
        descriptions = []
        for message in linter.check_files(fp.name):
            error_id, rule_desc = linter.parse_id_and_desc(message)
            error_ids.append(error_id)
            descriptions.append(rule_desc)

    assert 'E103' in error_ids
    assert 'deprecated sudo' in ' '.join(descriptions).lower()


ANSIBLELINT_TEST_FILE_FAIL_APP = """
---
- name: Test playbook
  tasks:
  - name: Copy local file to remote
    sudo: true
    copy:
      src: vars.yml
      dest: {{ dest_proj_path }}/config/ansible/vars.yml
"""


def test_ansiblelint_fail_app_exception():
    with tempfile.NamedTemporaryFile('w', suffix='.yaml') as fp:
        fp.write(ANSIBLELINT_TEST_FILE_FAIL_APP)
        fp.flush()

        linter = linters.AnsibleLinter()
        result = list(linter.check_files(fp.name))
    assert 'exception running ansible-lint' in ' '.join(result).lower()


# FLAKE8_ERROR_ID_REGEXP = r'^[EFW][0-9]{3}$'
# ANSIBLE_LINT_ERROR_ID_REGEXP = r'^E[0-9]{3}$'


def test_ansiblelint_error_id_match():
    linter = linters.AnsibleLinter()
    msg_e301 = 'playbook.yml:7: [E301] Commands should not change things if'
    msg_e105 = 'playbook.yml:16: [E105] Deprecated module docker'
    msg_e703 = '. [E703] meta/main.yml default values should be changed'

    error_id, _ = linter.parse_id_and_desc(msg_e301)
    assert error_id == 'E301'

    error_id, _ = linter.parse_id_and_desc(msg_e105)
    assert error_id == 'E105'

    error_id, _ = linter.parse_id_and_desc(msg_e703)
    assert error_id == 'E703'


def test_ansiblelint_error_id_not_match():
    linter = linters.AnsibleLinter()
    messages = [
        '[DEPRECATION WARNING]: docker is kept for backwards compatibility',
        '',
        'playbook.yml:7: [W301] Non-E prefix',
        'playbook.yml:7: [E1001] More than 3 numbers',
        'playbook.yml:7: E301 No brackets',
        'Syntax Error while loading YAML.',
        '[E403] Package installs should use state=present',
    ]

    for msg in messages:
        error_id, _ = linter.parse_id_and_desc(msg)
        assert error_id is None
