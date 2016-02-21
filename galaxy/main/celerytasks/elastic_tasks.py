# (c) 2015, Ansible, Inc. <support@ansible.com>
#
#  Tasks for maintaining non-haystack elasticsearch indexes
#

from celery import task

# local
from galaxy.main.models import Platform, Role, Tag
from galaxy.main.search_models import TagDoc, PlatformDoc, UserDoc
from galaxy.main.utils.memcache_lock import memcache_lock, MemcacheLockException


def update_tags(tags, logger):
    for tag in tags:
        logger.info("TAG: %s" % tag)
        try:
            with memcache_lock("tag_%s" % tag):
                pg_tag = Tag.objects.get(name=tag)
                es_tags = TagDoc.search().query('match', tag=tag).execute()
                cnt = pg_tag.get_num_roles() if pg_tag else 0
                updated = False    
                
                for es_tag in es_tags:
                    if es_tag.tag == tag:
                        updated = True
                        if cnt > 0:
                            if es_tag.roles != cnt:
                                logger.info("TAG: %s update count %d" % (tag, cnt))
                                try:
                                    es_tag.update(roles=cnt)
                                except Exception, e:
                                    logger.error("TAG: %s failed to update %s" % (tag, str(e.args)))
                                    raise
                            else:
                                logger.info("TAG: %s no update required" % tag)
                        else:
                            logger.info("TAG: %s delete" % tag)
                            try:
                                es_tag.delete()
                            except Exception, e:
                                logger.error("TAG: %s failed to delete %s" % (tag, str(e.args)))
                                raise

                if not updated:
                    # new tag
                    try:
                        logger.info("TAG: %s add" % tag)
                        doc = TagDoc(tag=pg_tag.name, roles=cnt)
                        doc.meta.id = pg_tag.id
                        doc.save()
                    except Exception, e:
                        logger.error("TAG: %s failed to add %s" % (tag, str(e.args)))
                        raise

        except MemcacheLockException, e:
            logger.info("TAG: %s unable to get lock %s" % (tag, str(e.args)))


def update_platforms(platforms, logger):
    for platform in platforms:
        logger.info("PLATFORM: %s" % platform)
        try:
            with memcache_lock("platform_%s" % platform):      
                cnt = Role.objects.filter(active=True, is_valid=True, platforms__name=platform) \
                    .order_by('namespace','name') \
                    .distinct('namespace', 'name').count()
                es_platforms = PlatformDoc.search().query('match', name=platform).execute()
                updated = False
                
                for es_platform in es_platforms:
                    if es_platform.name == platform:
                        updated = True
                        if es_platform.roles != cnt:
                            logger.info("PLATFORM: %s update count %s" % (platform, cnt))
                            try:
                                es_platform.update(roles=cnt)
                            except Exception, e:
                                logger.error("PLATFORM: %s failed to update %s" % (platform, str(e.args)))
                                raise
                        else:
                            logger.info("PLATFORM: no update required %s" % platform)

                if not updated:
                    # new platform
                    try:
                        logger.info("PLATFORM: %s add" % platform)
                        releases = [p.release for p in Platform.objects.filter(active=True, name=platform)
                                    .order_by('release').distinct('release').all()]
                        doc = PlatformDoc(
                            name=platform,
                            releases=releases,
                            roles=cnt,
                        )
                        doc.save()
                    except Exception, e:
                        logger.error("PLATFORM: %s failed to add %s" % (platform, str(e.args)))
                        raise
        except MemcacheLockException:
            logger.info("PLATFORM: %s failed to get lock %s" % (platform, str(e.args)))


def update_users(user, logger):
    logger.info("USER: %s" % user)
    try:
        with memcache_lock("user_%s" % user):      
            es_users = UserDoc.search().query('match', username=user).execute()
            updated = False    
            
            for es_user in es_users:
                if es_user.username == user:
                    logger.info("USER: %s already exists" % user)
                    updated = True
            
            if not updated:
                # new tag
                try:
                    logger.info("USER: %s add" % user)
                    doc = UserDoc(uername=user)
                    doc.save()
                except Exception, e:
                    logger.error("USER: %s failed to add %s" % (user, str(e.args)))
                    raise
    except MemcacheLockException, e:
        logger.info("USER: %s failed to get lock for %s" % (user, str(e.args)))


@task(throws=(Exception,), name="galaxy.main.celerytasks.elastic_tasks.update_custom_indexes")
def update_custom_indexes(username=None, tags=[], platforms=[]):

    logger = update_custom_indexes.get_logger()

    if len(tags) > 0:
        update_tags(tags, logger)
    
    if len(platforms) > 0:
        update_platforms(platforms, logger)
    
    if username is not None:
        update_users(username, logger)
