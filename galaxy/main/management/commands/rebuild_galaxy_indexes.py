from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

# elasticsearch
from elasticsearch_dsl import Index

# local
from galaxy.main.models import Platform, Role
from galaxy.main.search_models import TagDoc, PlatformDoc

class Command(BaseCommand):
    help = 'Rebuild custom elasticsearch indexes: galaxy_platforms, galaxy_tags'
    
    def handle(self, *args, **options):
        self.rebuild_tags()
        self.rebuild_platforms()
    
    def rebuild_tags(self):
        galaxy_tags = Index('galaxy_tags')
        galaxy_tags.settings(
            number_of_shards = 1
        )
        galaxy_tags.doc_type(TagDoc)
        galaxy_tags.delete(ignore=404)
        galaxy_tags.create()
        
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
            doc = TagDoc(tag=key, roles=value)
            doc.meta.id = cnt
            doc.save()
            cnt += 1


    def rebuild_platforms(self):
        galaxy_platforms = Index('galaxy_platforms')
        galaxy_platforms.settings(
            number_of_shards=1
        )

        galaxy_platforms.doc_type(PlatformDoc)
        galaxy_platforms.delete(ignore=404)
        galaxy_platforms.create()

        cnt = 0
        for platform in Platform.objects.filter(active=True).distinct('name').all():
            # self.es.create(index='galaxy_platforms', doc_type="platform", body=doc, id=cnt)
            doc = PlatformDoc(
                name=platform.name,
                release=[p.release for p in Platform.objects.filter(active=True, name=platform.name).order_by('release').distinct('release').all()],
                roles=Role.objects.filter(active=True, is_valid=True, platforms__name=platform.name).order_by('owner__username','name').distinct('owner__username','name').count(),
            )
            doc.meta.id = cnt
            doc.save()
            cnt += 1
