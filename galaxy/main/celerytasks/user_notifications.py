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
import celery

from galaxy.main import models
from django.contrib.sites.models import Site
from django.conf import settings
from django.core import mail
from allauth.account.models import EmailAddress


LOG = logging.getLogger(__name__)


class NotificationManger(object):
    from_email = 'notifications@galaxy.ansible.com'

    def __init__(self, email_template, preferences_name, user_list, subject,
                 db_message=None, repo=None):
        self.email_template = email_template
        self.preferences_name = preferences_name
        self.user_list = user_list
        self.subject = subject
        self.url = settings.GALAXY_URL.format(
            Site.objects.get_current().domain
        )

        self.repo = repo
        if db_message is None:
            self.db_message = subject
        else:
            self.db_message = db_message

    def render_email(self, context):
        text = self.email_template.format(**context)
        footer = email_footer_template.format(
            preferences_link='%s/preferences/' % (self.url)
        )

        return text + footer

    def send(self, email_message):
        for user in self.user_list:
            models.UserNotification.objects.create(
                user=user.user,
                type=self.preferences_name,
                message=self.db_message,
                repository=self.repo
            )

            if self.preferences_name not in user.preferences:
                continue

            if user.preferences[self.preferences_name]:
                email = EmailAddress.objects.filter(
                    primary=True,
                    user=user.user,
                )

                mail.send_mail(
                    self.subject,
                    email_message,
                    self.from_email,
                    [email[0].email],
                    fail_silently=True
                )

    def notify(self, context):
        email = self.render_email(context)
        self.send(email)


def import_status():
    pass


@celery.task
def collection_update(repo_id):
    followers = models.UserPreferences.objects.filter(
        repositories_followed__pk=repo_id
    )

    repo = models.Repository.objects.get(id=repo_id)
    author = repo.provider_namespace.namespace.name

    notification = NotificationManger(
        email_template=update_collection_template,
        preferences_name='notify_content_release',
        user_list=followers,
        subject='Ansible Galaxy: New version of ' + repo.name,
        db_message='A new version of %s.%s is available.' % (author, repo.name)
    )

    path = '/%s/%s/' % (repo.provider_namespace.namespace.name, repo.name)

    ctx = {
        'namespace_name': author,
        'content_name': repo.name,
        'content_url': notification.url + path
    }

    notification.notify(ctx)


@celery.task
def author_release(repo_id):
    repo = models.Repository.objects.get(id=repo_id)
    namespace = repo.provider_namespace.namespace
    followers = models.UserPreferences.objects.filter(
        namespaces_followed=namespace
    )

    author = repo.provider_namespace.namespace.name

    notification = NotificationManger(
        email_template=author_release_template,
        preferences_name='notify_author_release',
        user_list=followers,
        subject='Ansible Galaxy: %s has released a new collection' % (author),
        db_message='New release from {author}: {author}.{name}'.format(
            author=author,
            name=repo.name
        )
    )

    path = '/%s/%s/' % (author, repo.name)
    ctx = {
        'author_name': author,
        'content_name': repo.name,
        'content_url': notification.url + path,
    }

    notification.notify(ctx)


def new_survey():
    pass


import_status_template = '''Hello,

This message is to notify you that a recent import of {content_name} on \
Ansible galaxy has {status}.
'''


update_collection_template = '''Hello,

{namespace_name} has just released a new version of {content_name} on \
Ansible Galaxy. To see the new version, visit {content_url}.
'''


author_release_template = '''Hello,

One of the author's ({author_name}) that you are following on Ansible Galaxy \
has just released a new collection named {content_name}. To see it, visit \
{content_url}.
'''


new_survey_template = '''Hello,

Someone has just submitted a new rating for {content_name} on Ansible Galaxy.\
Your {content_type} now has a user rating of {content_score}. Visit \
{content_url} for more details.
'''


email_footer_template = '''
Cheers,
   Ansible Galaxy

-- To stop seeing these messages, visit {preferences_link} to update your \
settings.'''
