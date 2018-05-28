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

from .apb import APBLoader
from .module import ModuleLoader
from .module_utils import ModuleUtilsLoader
from .plugin import PluginLoader
from .role import RoleLoader


ALL_LOADERS = [
    APBLoader,
    ModuleLoader,
    ModuleUtilsLoader,
    PluginLoader,
    RoleLoader,
]


def get_loader(content_type):
    """Returns loader class for specified content type.

    :type content_type: constants.ContentType
    :param content_type: Content type.
    :returns: Loader class for specified content type.
    :raise ValueError: If no loader found for specified content type.
    """
    for loader_cls in ALL_LOADERS:
        content_types = loader_cls.content_types
        if not isinstance(loader_cls.content_types, (list, tuple)):
            content_types = [content_types]
        if content_type in content_types:
            return loader_cls
    raise ValueError('Loader for content type "{0}" not found'
                     .format(content_type))
