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

from haystack.backends import BaseEngine
from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend, ElasticsearchSearchQuery


class GalaxyElasticSearchBackend(ElasticsearchSearchBackend):

    # Settings to add an n-gram & edge n-gram analyzer.
    DEFAULT_SETTINGS = {
        'settings': {
            "analysis": {
                "analyzer": {
                    "ngram_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["haystack_ngram", "lowercase"]
                    },
                    "edgengram_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["haystack_edgengram", "lowercase"]
                    }
                },
                "tokenizer": {
                    "haystack_ngram_tokenizer": {
                        "type": "nGram",
                        "min_gram": 3,
                        "max_gram": 15,
                    },
                    "haystack_edgengram_tokenizer": {
                        "type": "edgeNGram",
                        "min_gram": 3,
                        "max_gram": 15,
                        "side": "front"
                    }
                },
                "filter": {
                    "haystack_ngram": {
                        "type": "nGram",
                        "min_gram": 3,
                        "max_gram": 15
                    },
                    "haystack_edgengram": {
                        "type": "edgeNGram",
                        "min_gram": 3,
                        "max_gram": 15
                    }
                }
            }
        }
    }


class ElasticsearchSearchEngine(BaseEngine):
    backend = GalaxyElasticSearchBackend
    query = ElasticsearchSearchQuery
