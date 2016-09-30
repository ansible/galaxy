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

import logging

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

# allauth
from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialToken

# local
from galaxy.main.models import ImportTask, Repository
from galaxy.main.celerytasks.tasks import refresh_user_repos, refresh_user_stars


logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(user_logged_in)
def user_logged_in_handler(request, user, **kwargs):
    if user.repositories.count() > 1:
        # User has entries in cache already, so no need to delay the login process.
        user.cache_refreshed = True
        user.save()
    else:
        # No entries found in cache, wait for a refresh to happen.
        user.cache_refreshed = False
        user.save()
    try:
        # Kick off a refresh
        token = SocialToken.objects.get(account__user=user, account__provider='github')
        refresh_user_repos.delay(user,token.token)
        refresh_user_stars.delay(user,token.token)
    except ObjectDoesNotExist:
        user.cache_refreshed = True
        user.save()
    except MultipleObjectsReturned:
        logger.error(u'Found multiple GitHub tokens for user: {}'.format(user.username).encode('utf-8').strip())
        user.cache_refreshed = True
        user.save()


@receiver(post_save, sender=ImportTask)
def import_task_post_save(sender, **kwargs):
    ''' 
    When a role is imported enable the role in the user's repository cache
    '''
    instance = kwargs['instance']
    for repo in Repository.objects.filter(github_user=instance.github_user,github_repo=instance.github_repo):
        repo.is_enabled = True
        repo.save()
