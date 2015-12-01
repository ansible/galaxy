import datetime
import re
import json 

from haystack import indexes
from galaxy.main.models import Role, Platform


class RoleIndex(indexes.SearchIndex, indexes.Indexable):
    role_id = indexes.IntegerField(model_attr='id')
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
    text = indexes.CharField(document=True, use_template=True)
    autocomplete = indexes.EdgeNgramField(use_template=True)
    platforms_autocomplete = indexes.EdgeNgramField(default='')
    tags_autocomplete = indexes.EdgeNgramField(default='')
    username_autocomplete = indexes.EdgeNgramField(model_attr='namespace')
    travis_status_url = indexes.CharField(model_attr='travis_status_url', default='', indexed=False)
    issue_tracker_url = indexes.CharField(model_attr='issue_tracker_url', default='', indexed=False)
    stargazers_count = indexes.IntegerField(model_attr='stargazers_count')
    watchers_count = indexes.IntegerField(model_attr='watchers_count')
    forks_count = indexes.IntegerField(model_attr='forks_count',indexed=False)
    open_issues_count = indexes.IntegerField(model_attr='open_issues_count',indexed=False)
    min_ansible_version = indexes.CharField(model_attr='min_ansible_version', default='1.2', indexed=False)
    user_is_subscriber = indexes.BooleanField(default=False, indexed=False)
    user_is_stargazer = indexes.BooleanField(default=False, indexed=False)
    download_count = indexes.IntegerField(model_attr='download_count')
    readme_html = indexes.CharField(model_attr='readme',default='',indexed=False)

    def get_model(self):
        return Role

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(active=True, is_valid=True)

    def prepare_platforms(self, obj):
        return [platform.name for platform in obj.platforms.filter(active=True).order_by('name').distinct('name')]

    def prepare_tags(self, obj):
        return obj.get_tags()

    def prepare_average_score(self, obj):
        return round(obj.average_score,1)

    #def prepare_sort_name(self, obj):
    #    return re.sub(r'[-\.]','',obj.name)

    def prepare_platforms_autocomplete(self, obj):
        return "%s %s %s" % (
            ' '.join(obj.get_unique_platforms()), 
            ' '.join(obj.get_unique_platform_search_terms()),
            ' '.join(obj.get_unique_platform_versions())
            )
    
    def prepare_tags_autocomplete(self, obj):
        return ' '.join(obj.get_tags())

    def prepare_versions(self, obj):
        result = [{ 'name': version.name, 'release_date': version.release_date.strftime('%Y-%m-%dT%H:%M:%S')} for version in obj.versions.filter(active=True).order_by('-name')]
        return json.dumps(result)

    def prepare_dependencies(self, obj):
        result = [{ 'name': dep.name, 'namespace': dep.namespace, 'id': dep.id } for dep in obj.dependencies.filter(active=True).order_by('namespace','name')]
        return json.dumps(result)

    def prepare_platform_details(self, obj):
        result = [{ 'name': plat.name, 'release': plat.release } for plat in obj.platforms.filter(active=True).order_by('name','release')]
        return json.dumps(result)

