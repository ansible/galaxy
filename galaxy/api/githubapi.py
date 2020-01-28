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

# FIXME(cutwater): This module is deprecated. It should be moved
#   to `galaxy.api.v1` package and eventually removed.
import logging

from github import Github
from github.GithubException import GithubException

from allauth.socialaccount.models import SocialToken
from django.core.exceptions import ObjectDoesNotExist
from galaxy.common.github import get_github_api_url
from galaxy.main.models import Provider


logger = logging.getLogger(__name__)


class GithubAPI(object):

    def __init__(self, user=None):
        self.user = user
        self.client = self.get_client()
        provider = self.get_provider()
        self.provider_name = provider.name
        self.provider_id = provider.id

    @staticmethod
    def get_provider():
        try:
            provider = Provider.objects.get(name__iexact='github', active=True)
        except ObjectDoesNotExist:
            raise Exception(
                "No provider found for GitHub"
            )
        return provider

    def get_client(self):
        try:
            gh_token = SocialToken.objects.get(account__user=self.user,
                                               account__provider='github')
        except ObjectDoesNotExist:
            raise Exception(
                "User does not have a GitHub OAuth token"
            )
        try:
            client = Github(base_url=get_github_api_url(),
                            login_or_token=gh_token.token)
        except GithubException as exc:
            raise Exception("Failed to connect to the GitHub API {0} - {1}"
                            .format(exc.data, exc.status))
        return client

    def user_namespaces(self):
        """ Return a list of user namespaces """
        result = []
        try:
            gh_user = self.client.get_user()
            source = {
                'name': gh_user.login,
                'description': gh_user.bio,
                'provider': self.provider_name.lower(),
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
                    'description': (org.description
                                    if hasattr(org, 'description') else None),
                    'provider': self.provider_name.lower(),
                    'display_name': org.name,
                    'avatar_url': org.avatar_url,
                    'location': org.location,
                    'company': org.company,
                    'email': org.email,
                    'html_url': org.blog,
                    'followers': org.followers
                }
                result.append(source)
        except GithubException as exc:
            raise Exception("Failed to access GitHub authorized user."
                            " {0} - {1}".format(exc.data, exc.status))
        return result

    def get_namespace_repositories(self, provider_namespace, name=None):
        """ Return a list of repositories for a given namespace """
        gh_user = self.client.get_user(login=provider_namespace)
        repos = []
        for gh_repo in gh_user.get_repos(type='public'):
            repo = {
                'provider_id': self.provider_id,
                'provider': self.provider_name.lower(),
                'provider_namespace': provider_namespace,
                'name': gh_repo.name,
                'description': gh_repo.description,
                'default_branch': gh_repo.default_branch,
                'stargazers_count': gh_repo.stargazers_count,
                'open_issues_count': gh_repo.open_issues_count,
                'forks_count': gh_repo.forks_count
            }

            if not name:
                repos.append(repo)
            elif gh_repo.name == name:
                try:
                    commits = gh_repo.get_commits()
                    commit = commits[0].commit
                except GithubException:
                    repo['commit'] = None
                    repo['commit_message'] = None
                    repo['commit_url'] = None
                    repo['commit_created'] = None
                else:
                    repo['commit'] = commit.sha
                    repo['commit_message'] = commit.message
                    repo['commit_url'] = commit.url
                    repo['commit_created'] = commit.author.date
                repo['watchers_count'] = 0
                for _ in gh_repo.get_subscribers():
                    repo['watchers_count'] += 1
                repos.append(repo)
                break

        return repos
