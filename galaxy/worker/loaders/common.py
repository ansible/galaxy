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

import ast

import yaml


def parse_ast_doc(node):
    # type: (ast.Str) -> dict
    """Parses documentation from python AST string node.

    :param ast.Str node: An AST string node.
    :rtype: dict
    :return: Documentation dictionary.
    :raises ValueError: if cannot parse documentation
            (e.g. documentation is not a valid yaml dictionary)
    """
    if not isinstance(node.value, ast.Str):
        raise ValueError('Invalid field type, string expected')

    try:
        documentation = yaml.safe_load(node.value.s)
    except yaml.YAMLError as e:
        raise ValueError(e)

    if not isinstance(documentation, dict):
        raise ValueError('Invalid YAML document, dictionary expected')
    return documentation
