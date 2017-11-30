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
    def default_login_redirect_url(self, request):
        if hasattr(settings, 'LOGIN_REDIRECT_URL'):
            return settings.LOGIN_REDIRECT_URL
        else:
            return '/'

    def get_login_redirect_url(self, request):
        if request.user.is_authenticated():
            for account in request.user.socialaccount_set.all():
                if account.provider == 'github':
                    return self.default_login_redirect_url(request)
            return '/accounts/connect'
        else:
            return self.default_login_redirect_url(request)
