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


from github import Github
from github.GithubException import GithubException

from allauth.socialaccount.models import SocialToken
from django.core.exceptions import ObjectDoesNotExist
from galaxy.main.models import Provider


class GithubAPI(object):

    def __init__(self, user=None, provider_name=None):
        self.user = user
        self.client = self.get_client()
        self.provider_name = provider_name if provider_name else self.get_provider_name()

    def get_provider_name(self):
        try:
            provider = Provider.objects.get(name__iexact='github', active=True)
        except ObjectDoesNotExist:
            raise Exception(
                "No provider found for GitHub"
            )
        return provider.name

    def get_client(self):
        try:
            gh_token = SocialToken.objects.get(account__user=self.user, account__provider='github')
        except ObjectDoesNotExist:
            raise Exception(
                "User does not have a GitHub OAuth token"
            )
        try:
            client = Github(gh_token.token)
        except GithubException as exc:
            raise Exception(
                "Failed to connect to the GitHub API {0} - {1}".format(exc.data, exc.status)
            )
        return client

    def user_namespaces(self):
        """ Return a list of user namespaces """
        result = []
        try:
            gh_user = self.client.get_user()
            source = {
                'name': gh_user.login,
                'description': gh_user.bio,
                'provider': self.provider_name,
                'display_name': gh_user.name,
                'avatar_url': gh_user.avatar_url,
                'location': gh_user.location,
                'company': gh_user.company,
                'email': gh_user.email,
                'html_url': gh_user.blog,
                'followers': gh_user.followers
            }
            result.append(source)

            gh_orgs = gh_user.get_orgs()
            for org in gh_orgs:
                source = {
                    'name': org.login,
                    'description': org.description if hasattr(org, 'description') else None,
                    'provider': self.provider_name,
                    'display_name': org.name,
                    'avatar_url': org.avatar_url,
                    'location': org.location,
                    'company': org.company,
                    'email': org.email,
                    'html_url': org.blog,
                    'followers': org.followers
                }
                result.append(source)
        except GithubException, exc:
            raise Exception(
                "Failed to access GitHub authorized user. {0} - {1}".format(exc.data, exc.status)
            )
        return result
