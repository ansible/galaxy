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
        galaxy_users.doc_type(UserDoc)
        galaxy_users.delete(ignore=404)
        galaxy_users.create()
        
        for role in Role.objects.filter(active=True, is_valid=True).order_by('owner__username').distinct('owner__username').all():
            doc = UserDoc(username=role.owner.username)
            doc.save()
        
    def rebuild_tags(self):
        galaxy_tags = Index('galaxy_tags')
        galaxy_tags.doc_type(TagDoc)
        galaxy_tags.delete(ignore=404)
        galaxy_tags.create()
        
        for tag in Tag.objects.filter(active=True).all():
            doc = TagDoc(tag=tag.name, roles=tag.get_num_roles())
            doc.meta.id = tag.id
            doc.save()

    def rebuild_platforms(self):
        galaxy_platforms = Index('galaxy_platforms')
        
        galaxy_platforms.doc_type(PlatformDoc)
        galaxy_platforms.delete(ignore=404)
        galaxy_platforms.create()

        for platform in Platform.objects.filter(active=True).distinct('name').all():
            alias_list = [alias for alias in self.get_platform_search_terms(platform.name)]
            alias_list = '' if len(alias_list) == 0 else alias_list
            release_list = [p.release for p in Platform.objects.filter(active=True, name=platform.name).order_by('release').distinct('release').all()]
            doc = PlatformDoc(
                name=platform.name,
                releases= release_list,
                roles=Role.objects.filter(active=True, is_valid=True, platforms__name=platform.name).order_by('owner__username','name').distinct('owner__username','name').count(),
                alias=alias_list,
                autocomplete="%s %s %s" % (platform.name, ' '.join(release_list), ' '.join(alias_list))
            )
            doc.save()
        
    def get_platform_search_terms(self, name):
        '''
        Fetch the unique set of aliases for a given platform
        '''
        terms = []
        for platform in Platform.objects.filter(active=True, name=name).all():
            if platform.alias:
                terms += platform.alias.split(' ')
        return set(terms)

