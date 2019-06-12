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

import logging

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from allauth.account.signals import user_logged_in
from allauth.socialaccount import models as auth_models

from galaxy import constants
from galaxy.main import models


logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(user_logged_in)
def user_logged_in_handler(request, user, **kwargs):
    social = auth_models.SocialAccount.objects.get(
        provider=constants.PROVIDER_GITHUB.lower(), user=user)
    user.avatar_url = social.extra_data.get('avatar_url')
    user.save()

    username = social.extra_data.get('login')
    sanitized_username = username.lower().replace('-', '_')

    if models.ProviderNamespace.objects.filter(name=username).exists():
        return

    # User is not associated with any Provider Namespaces, so we'll attempt
    # to create one, along with associated Namespace.

    # if name doesn't exist, set it to login
    name = social.extra_data.get('name') or username

    defaults = {
        'description': name,
        'avatar_url': social.extra_data.get('avatar_url'),
        'location': social.extra_data.get('location'),
        'company': social.extra_data.get('company'),
        'email': None,
        'html_url': social.extra_data.get('blog'),
    }

    ns_defaults = {'name': sanitized_username, **defaults}

    # Create lowercase namespace if case insensitive get does not find match
    namespace, _ = models.Namespace.objects.get_or_create(
        name__iexact=sanitized_username, defaults=ns_defaults)

    namespace.owners.add(user)

    provider_ns_defaults = {
        'description': social.extra_data.get('bio') or name,
        'followers': social.extra_data.get('followers'),
        'display_name': name,
        **defaults,
    }
    provider = models.Provider.objects.get(name__iexact="github")

    models.ProviderNamespace.objects.get_or_create(
        namespace=namespace, name=username, provider=provider,
        defaults=provider_ns_defaults)


@receiver(post_save, sender=models.ImportTask)
def import_task_post_save(sender, **kwargs):
    """
    When a role is imported enable the role in the user's repository cache
    """
    instance = kwargs['instance']
    if getattr(instance, 'repository'):
        repo = instance.repository
        repo.is_enabled = True
        repo.save()
