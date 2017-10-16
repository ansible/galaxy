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

from datetime import datetime
from elasticsearch_dsl import DocType, String, Long, Date, MetaField, analyzer, token_filter

__all__ = ["TagDoc", "PlatformDoc", "UserDoc"]


autocomplete = analyzer(
    'autocomplete',
    tokenizer = 'standard',
    filter = ["lowercase", token_filter('autocomplete_filter', 'edgeNGram', min_gram=2, max_gram=20)]
)


class BaseSearchModel(DocType):
    created_on = Date(include_in_all=False)
    last_modified_on = Date(include_in_all=False)

    def save(self, **kwargs):
        if not self.created_on:
            self.created_on = datetime.now()
        self.last_modified_on = datetime.now()
        return super(BaseSearchModel,self).save(** kwargs)


class TagDoc(BaseSearchModel):
    tag = String(analyzer=autocomplete, search_analyzer='standard')
    roles = Long(include_in_all=False)

    class Meta:
        index = 'galaxy_tags'
        all = MetaField(enabled=True)
        dynamic = MetaField(enabled=False)


class PlatformDoc(BaseSearchModel):
    name = String()
    releases = String()
    alias = String()
    roles = Long(include_in_all=False)
    autocomplete = String(analyzer=autocomplete, search_analyzer='standard')

    class Meta:
        index = 'galaxy_platforms'
        all = MetaField(enabled=True)
        dynamic = MetaField(enabled=False)


class UserDoc(BaseSearchModel):
    username = String(analyzer=autocomplete, search_analyzer='standard')

    class Meta:
        index = 'galaxy_users'
        all = MetaField(enabled=False)
        dynamic = MetaField(enabled=False)
