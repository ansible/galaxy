import datetime
import re
from haystack import indexes
from galaxy.main.models import Role, Platform


class RoleIndex(indexes.SearchIndex, indexes.Indexable):
    id = indexes.IntegerField(model_attr='id')
    username = indexes.CharField(model_attr='namespace')
    name = indexes.CharField(model_attr='name', faceted=True)
    description = indexes.CharField(model_attr='description')
    github_user = indexes.CharField(model_attr='github_user')
    github_repo = indexes.CharField(model_attr='github_repo')
    github_branch = indexes.CharField(model_attr='github_branch')
    tags = indexes.MultiValueField(default='', faceted=True)
    platforms = indexes.MultiValueField(default='', faceted=True)
    created = indexes.DateTimeField(model_attr='created', default='')
    modified = indexes.DateTimeField(model_attr='modified', default='')
    imported = indexes.DateTimeField(model_attr='imported', default=None)
    text = indexes.CharField(document=True, use_template=True)
    autocomplete = indexes.EdgeNgramField(use_template=True)
    platforms_autocomplete = indexes.EdgeNgramField(default='')
    tags_autocomplete = indexes.EdgeNgramField(default='')
    username_autocomplete = indexes.EdgeNgramField(model_attr='namespace')
    travis_status_url = indexes.CharField(model_attr='travis_status_url')
    stargazers_count = indexes.IntegerField(model_attr='stargazers_count')
    watchers_count = indexes.IntegerField(model_attr='watchers_count')
    forks_count = indexes.IntegerField(model_attr='forks_count')
    open_issues_count = indexes.IntegerField(model_attr='open_issues_count')
    user_is_subscriber = indexes.BooleanField(default=False)
    user_is_stargazer = indexes.BooleanField(default=False)
    download_count = indexes.IntegerField(model_attr='download_count')

    def get_model(self):
        return Role

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(active=True, is_valid=True)

    def prepare_platforms(self, obj):
        return [platform.name for platform in obj.platforms.filter(active=True).distinct('name')]

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
