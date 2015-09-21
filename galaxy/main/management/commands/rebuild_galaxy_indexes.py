from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

# elasticsearch
from elasticsearch_dsl import Index

# local
from galaxy.main.models import Platform, Tag, Role
from galaxy.main.search_models import TagDoc, PlatformDoc, UserDoc


class Command(BaseCommand):
    help = 'Rebuild custom elasticsearch indexes: galaxy_platforms, galaxy_tags'
    
    def handle(self, *args, **options):
        self.rebuild_tags()
        self.rebuild_platforms()
        self.rebuild_users()

    def rebuild_users(self):
        galaxy_users = Index('galaxy_users')
        galaxy_users.settings(
            number_of_shards = 1
        )
        galaxy_users.doc_type(UserDoc)
        galaxy_users.delete(ignore=404)
        galaxy_users.create()
        
        #cnt = 0
        for role in Role.objects.filter(active=True, is_valid=True).order_by('owner__username').distinct('owner__username').all():
            doc = UserDoc(username=role.owner.username)
            #doc.meta.id = cnt
            doc.save()
            #cnt += 1

    def rebuild_tags(self):
        galaxy_tags = Index('galaxy_tags')
        galaxy_tags.settings(
            number_of_shards = 1
        )
        galaxy_tags.doc_type(TagDoc)
        galaxy_tags.delete(ignore=404)
        galaxy_tags.create()
        
        for tag in Tag.objects.filter(active=True).all():
            doc = TagDoc(tag=tag.name, roles=tag.get_num_roles())
            doc.meta.id = tag.id
            doc.save()

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
                releases=[p.release for p in Platform.objects.filter(active=True, name=platform.name).order_by('release').distinct('release').all()],
                roles=Role.objects.filter(active=True, is_valid=True, platforms__name=platform.name).order_by('owner__username','name').distinct('owner__username','name').count(),
            )
            doc.meta.id = cnt
            doc.save()
            cnt += 1
