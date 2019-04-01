# (c) 2012-2019, Ansible by Red Hat
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
import pulpcore.exceptions as pulp_exc


class TaskError(pulp_exc.PulpException):
    error_code = 'GLW0000'
    message = 'Unknown task error.'

    def __init__(self, message=None, error_code=None):
        super().__init__(error_code or self.__class__.error_code)
        self.message = message or self.__class__.message

    def __str__(self):
        return self.message


class VersionConflict(TaskError):
    error_code = 'GLW0001'
    message = 'Version exists.'


class ImportFailed(TaskError):
    error_code = 'GLW0002'
    message = 'Import failed.'


# TODO(cutwater): This exception is part of the old celery worker and
#   should be removed once migration to Pulp's tasking system is complete.
class LegacyTaskError(Exception):
    pass
