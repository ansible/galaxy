# (c) 2012-2016, Ansible by Red Hat
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

import json

from haystack import indexes
from galaxy.main.models import Role


class RoleIndex(indexes.SearchIndex, indexes.Indexable):
    role_id = indexes.IntegerField(model_attr='id')
    role_type = indexes.CharField(model_attr='role_type')
    username = indexes.CharField(model_attr='namespace')
    name = indexes.CharField(model_attr='name', faceted=True)
    description = indexes.CharField(model_attr='description')
    github_user = indexes.CharField(model_attr='github_user', indexed=False)
    github_repo = indexes.CharField(model_attr='github_repo', indexed=False)
    github_branch = indexes.CharField(model_attr='github_branch', indexed=False)
    tags = indexes.MultiValueField(default='', faceted=True)
    platforms = indexes.MultiValueField(default='', faceted=True)
    platform_details = indexes.CharField(default='', indexed=False)
    versions = indexes.CharField(default='', indexed=False)
    dependencies = indexes.CharField(default='', indexed=False)
    created = indexes.DateTimeField(model_attr='created', default='', indexed=False)
    modified = indexes.DateTimeField(model_attr='modified', default='', indexed=False)
    imported = indexes.DateTimeField(model_attr='imported', default=None, null=True, indexed=False)
    last_commit_date = indexes.DateTimeField(model_attr='commit_created', default=None, null=True, indexed=False)
    text = indexes.CharField(document=True, use_template=True)
    autocomplete = indexes.EdgeNgramField(use_template=True)
    platforms_autocomplete = indexes.EdgeNgramField(default='')
    tags_autocomplete = indexes.EdgeNgramField(default='')
    username_autocomplete = indexes.EdgeNgramField(model_attr='namespace')
    travis_status_url = indexes.CharField(model_attr='travis_status_url', default='', indexed=False)
    travis_build_url = indexes.CharField(model_attr='travis_build_url', default='', indexed=False)
    issue_tracker_url = indexes.CharField(model_attr='issue_tracker_url', default='', indexed=False)
    stargazers_count = indexes.IntegerField(model_attr='stargazers_count')
    watchers_count = indexes.IntegerField(model_attr='watchers_count')
    forks_count = indexes.IntegerField(model_attr='forks_count', indexed=False)
    open_issues_count = indexes.IntegerField(model_attr='open_issues_count', indexed=False)
    min_ansible_version = indexes.CharField(model_attr='min_ansible_version', default='1.2', indexed=False)
    user_is_subscriber = indexes.BooleanField(default=False, indexed=False)
    user_is_stargazer = indexes.BooleanField(default=False, indexed=False)
    download_count = indexes.IntegerField(model_attr='download_count')

    def get_model(self):
        return Role

    def index_queryset(self, using=None):
        # Used when the entire index for model is updated
        return self.get_model().objects.filter(active=True, is_valid=True)

    def prepare_platforms(self, obj):
        return [
            'Enterprise_Linux' if platform.name == 'EL' else platform.name
            for platform in obj.platforms.filter(active=True).order_by('name').distinct('name')
        ]

    def prepare_tags(self, obj):
        return obj.get_tags()

    def prepare_average_score(self, obj):
        return round(obj.average_score, 1)

    def prepare_platforms_autocomplete(self, obj):
        return "%s %s %s" % (
            ' '.join(['Enterprise_Linux' if n == 'EL' else n for n in obj.get_unique_platforms()]),
            ' '.join(obj.get_unique_platform_search_terms()),
            ' '.join(obj.get_unique_platform_versions())
        )

    def prepare_tags_autocomplete(self, obj):
        return ' '.join(obj.get_tags())

    def prepare_versions(self, obj):
        result = []
        for version in obj.versions.filter(active=True).order_by('-loose_version'):
            release_date = version.release_date.strftime('%Y-%m-%dT%H:%M:%SZ') if version.release_date else None
            result.append({
                'name': version.name,
                'release_date': release_date
            })
        return json.dumps(result)

    def prepare_dependencies(self, obj):
        result = [
            dict(name=dep.name, namespace=dep.namespace, id=dep.id)
            for dep in obj.dependencies.filter(active=True).order_by('namespace', 'name')
        ]
        return json.dumps(result)

    def prepare_platform_details(self, obj):
        results = []
        for plat in obj.platforms.filter(active=True).order_by('name', 'release'):
            name = 'Enterprise_Linux' if plat.name == 'EL' else plat.name
            results.append(
                dict(name=name, release=plat.release)
            )
        return json.dumps(results)
