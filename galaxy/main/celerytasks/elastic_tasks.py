# (c) 2015, Ansible, Inc. <support@ansible.com>
#
#  Tasks for maintaining non-haystack elasticsearch indexes
#


from celery import task
from django.conf import settings

# local
from galaxy.main.models import Tag, Role
from galaxy.main.search_models import TagDoc, PlatformDoc


@task()
def update_tag(tag):
    print "TAG: %s" % tag
    pg_tag = Tag.objects.get(name=tag)
    es_tags = TagDoc.search().query('match', tag=tag).execute()
    cnt = pg_tag.get_num_roles() if pg_tag else 0
    updated = False    
    
    for es_tag in es_tags:
        if es_tag.tag == tag:
            updated = True
            if cnt > 0:
                if es_tag.roles != cnt:
                    print "TAG: update %s %d" % (tag,cnt)
                    try:
                        es_tag.update(roles=cnt)
                    except:
                        print "TAG: failed to update %s" % tag
                        raise
                else:
                    print "TAG: no update required %s" % tag
            else:
                print "TAG: delete %s" % tag
                try:
                    es_tag.delete()
                except:
                    print "TAG: failed to delete %s" % tag
                    raise

    if not updated:
        # new tag
        try:
            print "TAG: add %s" % tag
            doc = TagDoc(tag=pg_tag.name, roles=cnt)
            doc.meta.id = pg_tag.id
            doc.save()
        except:
            print 'TAG: exception failed to add %s' % tag
            raise

@task()
def update_platform(platform):
    print "PLATFORM: %s" % platform
    cnt = Role.objects.filter(active=True, is_valid=True, platforms__name=platform).order_by('owner__username','name').distinct('owner__username','name').count(),
    es_platforms = PlatformDoc.search().query('match', name=platform).execute()
    updated = False
    
    for es_platform in es_platforms:
        if es_platform.name == platform:
            updated = True
            if es_platform.roles != cnt:
                print "PLATFORM: count update %s %d" % (platform, cnt)
                try:
                    es_platform.update(roles=cnt)
                except:
                    print "PLATFORM: failed to update %s" % platform
                    raise
            else:
                print "PLATFORM: no update required %s" % platform

    if not updated:
        # new platform
        try:
            print "Platform: add %s" % platform
            doc = PlatformDoc(
                name=platform,
                releases=[p.release for p in Platform.objects.filter(active=True, name=platform).order_by('release').distinct('release').all()],
                roles=cnt,
            )
            doc.save()
        except:
            print "PLATFORM: failed to add %s" % platform
            raise


    