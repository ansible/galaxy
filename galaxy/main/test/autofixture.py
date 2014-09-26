# (c) 2012-2014, Ansible, Inc. <support@ansible.com>
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from galaxy.main.models import Role
from autofixture import generators, register, AutoFixture

class RoleAutoFixture(AutoFixture):
    field_values = {
        'name': generators.StaticGenerator('role_name'),
        'github_user': generators.StaticGenerator('github_user'),
        'github_repo': generators.StaticGenerator('github_repo'),
    }

register(Role, RoleAutoFixture)
