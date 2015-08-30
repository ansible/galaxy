from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from galaxy.main.models import Platform, Role
from elasticsearch import Elasticsearch

class Command(BaseCommand):
    help = 'Rebuild custom elasticsearch indexes: galaxy_platforms, galaxy_tags'

    es = Elasticsearch([{ 'host': settings.ELASTIC_SEARCH['host'], 'port': settings.ELASTIC_SEARCH['port'], 'use_ssl': False }])
    
    def handle(self, *args, **options):
        self.rebuild_tags()
        self.rebuild_platforms()
    
    def rebuild_tags(self):
        if self.es.indices.exists('galaxy_tags'):
            self.es.indices.delete('galaxy_tags')
        
        galaxy_tags = {
            "settings": {
                "number_of_shards": 1,
                "analysis": {
                    "filter": {
                        "autocomplete_filter": {
                            "type": "edge_ngram",
                            "min_gram": 1,
                            "max_gram": 20
                        }
                    },
                    "analyzer": {
                        "autocomplete": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "autocomplete_filter"
                            ]
                        }
                    }
                }
            },
            "mappings": {
                "tag": {
                    "_all": { "enabled": True },
                    "dynamic": False,
                    "properties": {
                        "tag": {
                            "type": "string",
                            "index_analyzer": "autocomplete",
                            "search_analyzer": "standard"
                        },
                        "roles": {
                            "type": "long",
                            "include_in_all": False
                        }
                    }
                }
            }
        }
        
        self.es.indices.create('galaxy_tags', body=galaxy_tags)
        
        tags = {}
        for role in Role.objects.filter(active=True, is_valid=True).all():
            if role.tags:
                for tag in role.tags:
                    if tag in tags:
                        tags[tag] += 1
                    else:
                        tags[tag] = 1

        cnt = 0
        for key, value in tags.items():
            self.es.create(index='galaxy_tags', doc_type="tag", body={ "tag": key, "roles": value }, id=cnt)
            cnt += 1


    def rebuild_platforms(self):
        if self.es.indices.exists('galaxy_platforms'):
            self.es.indices.delete('galaxy_platforms')
        
        galaxy_platforms = {
            "settings": {
                "number_of_shards": 1,
                "analysis": {
                    "filter": {
                        "autocomplete_filter": {
                            "type": "edge_ngram",
                            "min_gram": 1,
                            "max_gram": 20
                        }
                    },
                    "analyzer": {
                        "autocomplete": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "autocomplete_filter"
                            ]
                        }
                    }
                }
            },
            "mappings": {
                "platform": {
                    "_all": { "enabled": True },
                    "dynamic": False,
                    "properties": {
                        "name": {
                            "type": "string",
                            "index_analyzer": "autocomplete",
                            "search_analyzer": "standard"
                        },
                        "releases": {
                           "type": "string",
                           "index_analyzer": "autocomplete",
                           "search_analyzer": "standard"
                        },
                        "roles": {
                            "type": "long",
                            "include_in_all": False
                        }    
                    }
                }
            }
        }
        
        self.es.indices.create('galaxy_platforms', body=galaxy_platforms)
        
        cnt = 0
        for platform in Platform.objects.filter(active=True).distinct('name').all():
            doc = {
                "name": platform.name,
                "releases": [p.release for p in Platform.objects.filter(active=True, name=platform.name).order_by('release').distinct('release').all()],
                "roles": Role.objects.filter(active=True, is_valid=True, platforms__name=platform.name).order_by('owner__username','name').distinct('owner__username','name').count(),
            }
            self.es.create(index='galaxy_platforms', doc_type="platform", body=doc, id=cnt)
            cnt += 1



