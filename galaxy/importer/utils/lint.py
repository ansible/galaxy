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

import attr


@attr.s(slots=True)
class LintRecord:
    """
    A class that represents linter report record.

    :var type: Linter type (e.g. flake8, ansible-lint).
    :var code: Linter rule code (e.g. e101, importer101).
    :var message: Linter rule description string.
    :var score_type:
    :var severity: Rule severity
    """
    type = attr.ib(type=str)
    code = attr.ib(type=str)
    message = attr.ib(type=str)
    severity = attr.ib(type=int, default=0)
    score_type = attr.ib(type=str, default=None)
