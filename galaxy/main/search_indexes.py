import datetime
import re
from haystack import indexes
from galaxy.main.models import Role, Platform


class RoleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name', faceted=True)
    description = indexes.CharField(model_attr='description')
    tags = indexes.MultiValueField(default='', faceted=True)
    platforms = indexes.MultiValueField(default='', faceted=True)
    username = indexes.CharField(model_attr='namespace')
    average_score = indexes.FloatField(default=0)
    num_ratings = indexes.IntegerField(model_attr='num_ratings')
    created = indexes.DateTimeField(model_attr='created', default='')
    modified = indexes.DateTimeField(model_attr='modified', default='')
    sort_name = indexes.CharField(default='')
    github_user = indexes.CharField(model_attr='github_user')
    github_repo = indexes.CharField(model_attr='github_repo')
    github_branch = indexes.CharField(model_attr='github_branch')
    travis_status_url = indexes.CharField(model_attr='travis_status_url')
    
    # autocomplete fields
    autocomplete = indexes.EdgeNgramField(use_template=True)
    tags_autocomplete = indexes.EdgeNgramField(default='')
    platforms_autocomplete = indexes.EdgeNgramField(default='')
    username_autocomplete = indexes.EdgeNgramField(model_attr='namespace')


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

    def prepare_sort_name(self, obj):
        return re.sub(r'[-\.]','',obj.name)

    def prepare_platforms_autocomplete(self, obj):
        return "%s %s %s" % (
            ' '.join(obj.get_unique_platforms()), 
            ' '.join(obj.get_unique_platform_search_terms()),
            ' '.join(obj.get_unique_platform_versions())
            )
    
    def prepare_tags_autocomplete(self, obj):
        return ' '.join(obj.get_tags())
