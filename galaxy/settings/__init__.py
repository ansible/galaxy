# (c) 2012-2017, Ansible by Red Hat
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
# Django settings for galaxy project.

import inspect


def include_settings(filename, scope=None, optional=False):
    """
    Includes python settings file into specified scope.

    :param str filename: Python source file.
    :param scope: Destination scope, by default global scope of function caller
           is used.
    :param bool optional: If set to True no exception will be raised if
           file does not exist.
    """
    if scope is None:
        scope = inspect.stack()[1][0].f_globals

    try:
        fp = open(filename)
    except IOError:
        if optional:
            return
        raise

    with fp:
        exec(fp.read(), scope)
