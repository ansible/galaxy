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

import django.db.models.sql.aggregates
import django.db.models.aggregates
 
# Usage (to retrieve objects with highest average, NULLs become zeroes and are last):
# MyModel.objects.annotate(average=AvgWithZeroForNull('other_model__field_name')).order_by('-average')

class AvgWithZeroForNull(django.db.models.sql.aggregates.Avg):
    sql_template = 'COALESCE(%(function)s(%(field)s), 0)'
django.db.models.sql.aggregates.AvgWithZeroForNull = AvgWithZeroForNull
 
class AvgWithZeroForNull(django.db.models.aggregates.Avg):
    name = 'AvgWithZeroForNull'
django.db.models.aggregates.AvgWithZeroForNull = AvgWithZeroForNull

