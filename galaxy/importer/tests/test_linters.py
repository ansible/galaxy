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
    with tempfile.NamedTemporaryFile() as fp:
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
    with tempfile.NamedTemporaryFile() as fp:
        fp.write(FLAKE8_TEST_FILE_FAIL)
        fp.flush()

        linter = linters.Flake8Linter()
        result = list(linter.check_files(fp.name))

        expected = [
            "{0}:3:9: F821 undefined name 'x'",
            "{0}:6:9: F821 undefined name 'y'",
            "{0}:7:1: E101 indentation contains mixed spaces and tabs",
            "{0}:7:1: W191 indentation contains tabs",
        ]
        expected = [s.format(fp.name) for s in expected]
        assert sorted(result) == sorted(expected)


YAMLLINT_TEST_FILE_OK = """---
x:
  - y
  - z
"""


def test_yamllint_ok():
    with tempfile.NamedTemporaryFile() as fp:
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
    with tempfile.NamedTemporaryFile() as fp:
        fp.write(YAMLLINT_TEST_FILE_FAIL)
        fp.flush()

        linter = linters.YamlLinter()
        result = list(linter.check_files(fp.name))

        expected = [
            '{0}:1:1: [error] too many blank lines (1 > 0) (empty-lines)',
            '{0}:2:1: [warning] missing document start "---" (document-start)',
            '{0}:4:7: [error] too many spaces after hyphen (hyphens)',
        ]
        expected = [s.format(fp.name) for s in expected]
        assert sorted(result) == sorted(expected)
