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

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.signals import password_changed, password_set

from django.conf import settings
from django.contrib import messages
from django.dispatch import receiver

@receiver(password_changed)
def password_change_callback(sender, request, user, **kwargs):
    messages.success(request, 'You have successfully changed your password.')

@receiver(password_set)
def password_set_callback(sender, request, user, **kwargs):
    messages.success(request, 'You have successfully set your password.')

class AccountAdapter(DefaultAccountAdapter):
  def get_login_redirect_url(self, request):
      if hasattr(settings, 'LOGIN_REDIRECT_URL'):
          return settings.LOGIN_REDIRECT_URL
      else:
          return '/'
