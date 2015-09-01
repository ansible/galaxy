import datetime
from haystack import indexes
from galaxy.main.models import Role, Platform


class RoleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name', faceted=True)
    description = indexes.CharField(model_attr='description')
    tags = indexes.MultiValueField(model_attr='tags', default='', faceted=True)
    platforms = indexes.MultiValueField(default='', faceted=True)
    # readme = indexes.CharField(model_attr='readme', default='')
    username = indexes.CharField(model_attr='owner__username')
    average_score = indexes.FloatField(model_attr='average_score')
    num_ratings = indexes.IntegerField(model_attr='num_ratings')
    created = indexes.DateTimeField(model_attr='created', default='')
    modified = indexes.DateTimeField(model_attr='modified', default='')
    
    # autocomplete 
    autocomplete = indexes.EdgeNgramField(use_template=True)


    def get_model(self):
        return Role

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(active=True, is_valid=True)

    def prepare_platforms(self, obj):
        return [platform.name for platform in obj.platforms.filter(active=True).distinct('name')]
