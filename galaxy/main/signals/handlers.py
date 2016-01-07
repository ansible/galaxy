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

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, pre_save, pre_delete, post_save, post_delete
from django.contrib.auth import get_user_model

# elasticsearch
from elasticsearch_dsl import Search, Q

# allauth
from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialToken

# github
from github import Github, AuthenticatedUser

# local
from galaxy.main.models import Role, RoleRating, Tag, ImportTask, Repository
from galaxy.main.search_models import TagDoc, PlatformDoc
from galaxy.main.celerytasks.elastic_tasks import update_tags, update_platforms, update_users
from galaxy.main.celerytasks.tasks import refresh_user_repos, refresh_user_stars

User = get_user_model()


@receiver(user_logged_in)
def user_logged_in_handler(request, user, **kwargs):
    user.cache_refreshed = False
    user.save()
    # try:
    token = SocialToken.objects.get(account__user=user, account__provider='github')
    refresh_user_repos.delay(user,token.token)
    refresh_user_stars.delay(user,token.token)
    # except:
    #    pass

@receiver(post_save, sender=ImportTask)
def import_task_post_save(sender, **kwargs):
    ''' 
    Update user repository cache
    '''
    instance = kwargs['instance']
    for repo in Repository.objects.filter(github_user=instance.github_user,github_repo=instance.github_repo):
        repo.is_enabled = True
        repo.save()

@receiver(pre_save, sender=Role)
@receiver(pre_delete, sender=Role)
def role_pre_save(sender, **kwargs):
    '''
    Before changes are made to a role grab the list of associated tags. The list will be used on post save 
    to signal celery to update elasticsearch indexes.
    '''
    instance = kwargs['instance']
    tags = instance.get_tags() if instance.id else []
    platforms = instance.get_unique_platforms() if instance.id else []
    username = instance.namespace if instance.id else ''
    instance._saved_tag_names = tags
    instance._saved_username = username
    instance._saved_platforms = platforms


@receiver(post_save, sender=Role)
@receiver(post_delete, sender=Role)
def role_post_save(sender, **kwargs):
    '''
    Signal celery to update the indexes.
    '''
    instance = kwargs['instance']
    tags = getattr(instance, '_saved_tag_names', None)
    if tags:
        for tag in tags:
            update_tags.delay(tag)

    username = getattr(instance, '_saved_username', None)
    if username:
        update_users.delay(username)

    platforms = getattr(instance, '_saved_platforms', None)
    if platforms:
        for platform in platforms:
            update_platforms.delay(platform)

