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

import elasticsearch_dsl as es_dsl
from django.core.management import base

from galaxy.main import models
from galaxy.main import search_models


class Command(base.BaseCommand):
    help = ('Rebuild custom elasticsearch indexes: '
            'galaxy_platforms, galaxy_tags')

    def handle(self, *args, **options):
        self.rebuild_tags()
        self.rebuild_platforms()
        self.rebuild_cloud_platforms()
        self.rebuild_users()

    def rebuild_users(self):
        galaxy_users = es_dsl.Index('galaxy_users')
        galaxy_users.doc_type(search_models.UserDoc)
        galaxy_users.delete(ignore=404)
        galaxy_users.create()

        for role in (models.Content.objects
                     .filter(active=True, is_valid=True)
                     .order_by('namespace__name')
                     .distinct('namespace__name').all()):
            doc = search_models.UserDoc(username=role.namespace.name)
            doc.save()

    def rebuild_tags(self):
        galaxy_tags = es_dsl.Index('galaxy_tags')
        galaxy_tags.doc_type(search_models.TagDoc)
        galaxy_tags.delete(ignore=404)
        galaxy_tags.create()

        for tag in models.Tag.objects.filter(active=True).all():
            doc = search_models.TagDoc(tag=tag.name, roles=tag.get_num_roles())
            doc.meta.id = tag.id
            doc.save()

    def rebuild_platforms(self):
        galaxy_platforms = es_dsl.Index('galaxy_platforms')

        galaxy_platforms.doc_type(search_models.PlatformDoc)
        galaxy_platforms.delete(ignore=404)
        galaxy_platforms.create()

        for platform in (
                models.Platform.objects.filter(active=True)
                .distinct('name').all()):
            alias_list = [alias for alias in
                          self.get_platform_search_terms(platform.name)]
            alias_list = '' if len(alias_list) == 0 else alias_list

            platforms = (
                models.Platform.objects.filter(active=True, name=platform.name)
                .order_by('release').distinct('release').all())
            release_list = [p.release for p in platforms]

            if platform.name == 'EL':
                search_name = 'Enterprise_Linux'
            else:
                search_name = platform.name

            roles_count = (
                models.Content.objects.filter(
                    active=True, is_valid=True, platforms__name=platform.name)
                .order_by('namespace__name', 'content_type__name', 'name')
                .distinct('namespace__name', 'content_type__name', 'name')
                .count()
            )

            doc = search_models.PlatformDoc(
                name=search_name,
                releases=release_list,
                roles=roles_count,
                alias=alias_list,
                autocomplete="%s %s %s" % (
                    search_name,
                    ' '.join(release_list),
                    ' '.join(alias_list))
            )
            doc.save()

    def rebuild_cloud_platforms(self):
        index = es_dsl.Index('galaxy_cloud_platforms')

        index.doc_type(search_models.CloudPlatformDoc)
        index.delete(ignore=404)
        index.create()

        for platform in models.CloudPlatform.objects.filter(active=True).all():
            roles_count = (
                models.Content.objects
                .filter(active=True, is_valid=True,
                        cloud_platforms__name=platform.name)
                .order_by('namespace__name', 'content_type__name', 'name')
                .distinct('namespace__name', 'content_type__name', 'name')
                .count())
            doc = search_models.CloudPlatformDoc(
                name=platform.name,
                roles=roles_count,
                autocomplete=platform.name,
            )
            doc.save()

    def get_platform_search_terms(self, name):
        """Fetch the unique set of aliases for a given platform"""
        terms = []
        for platform in models.Platform.objects.filter(
                active=True, name=name).all():
            if platform.alias:
                terms += platform.alias.split(' ')
        return set(terms)
