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
from django.core.exceptions import ObjectDoesNotExist

# allauth
from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount

# local
from galaxy.main.models import ImportTask, Namespace, Provider, ProviderNamespace


logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(user_logged_in)
def user_logged_in_handler(request, user, **kwargs):
    if user.namespaces.count():
        # User is associated with one or more namespaces. Even though the Namespaces may be inactive, we'll
        # assume the user has been here before, and knows how to manage Namespaces
        return

    # User is not associated with any Namespaces, so we'll attempt to create one, along with associated Provider
    # Namespaces
    namespace = None
    for provider in Provider.objects.all():
        try:
            social = SocialAccount.objects.get(provider__iexact=provider.name.lower(), user=user)
        except ObjectDoesNotExist:
            continue

        if provider.name.lower() == 'github':
            login = social.extra_data.get('login')
            name = social.extra_data.get('name')
            defaults = {
                'description': name,
                'avatar_url': social.extra_data.get('avatar_url'),
                'location': social.extra_data.get('location'),
                'company': social.extra_data.get('company'),
                'email': social.extra_data.get('email'),
                'html_url': social.extra_data.get('blog'),
            }
            if not namespace:
                # Only create one Namespace
                namespace, _ = Namespace.objects.get_or_create(name=login, defaults=defaults)
                namespace.owners.add(user)
            defaults['description'] = social.extra_data.get('bio')
            defaults['followers'] = social.extra_data.get('followers')
            defaults['display_name'] = social.extra_data.get('name')
            ProviderNamespace.objects.get_or_create(namespace=namespace, name=login, provider=provider,
                                                    defaults=defaults)


@receiver(post_save, sender=ImportTask)
def import_task_post_save(sender, **kwargs):
    '''
    When a role is imported enable the role in the user's repository cache
    '''
    instance = kwargs['instance']
    repo = instance.repository
    repo.is_enabled = True
    repo.save()
