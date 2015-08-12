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

import datetime
import markdown as md

from django import template
from django.utils import timezone
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def querysort(value, arg):
   """
   Sorts a query set based on a field
   """
   value = value.order_by(arg)
   return value

@register.filter
def markdown(value):
   return md.markdown(value)

@register.filter
def firstwords(value, arg):
   arg = int(arg)
   return " ".join(value.split()[:arg])+"..."

@register.filter
def timesince(value):
   diff = timezone.now() - value
   plural = ""
   if diff.days == 0:
      hours = int(diff.seconds/3600.0)
      if hours != 1:
         plural = "s"
      return "%d hour%s ago" % (int(diff.seconds/3600.0), plural)
   else:
      if diff.days != 1:
         plural = "s"
      return "%d day%s ago" % (diff.days, plural)

@register.filter
@stringfilter
def urlname(value):
    parts = value.split('/')
    paths = []
    for part in parts:
        if not part == '':
           paths.append(part)
    if len(paths) > 1:
        return check_title("%s %s" % (paths[-2].title(), paths[-1].title()))
    elif len(paths) > 0:
        return check_title(paths[-1].title())
    else:
        return ''

def check_title(value):
    if value == 'Password Change':
        return 'Change Password'
    elif value == 'Accounts Connect':
        return 'Connect to Github'
    elif value == 'Role Add':
        return 'Add a Role'
    elif value == 'Accounts Login':
        return 'Login'
    elif value == 'Accounts Landing':
        return 'Success!'
    elif value == 'Accounts Logout':
        return 'Logout'
    elif 'Confirm-Email' in value:
        return 'Confirm Email'
    else:
        return value
