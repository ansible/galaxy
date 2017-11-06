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

from celery import task

# local
from galaxy.main.models import Platform, Role, Tag
from galaxy.main.search_models import TagDoc, PlatformDoc, UserDoc
from galaxy.main.utils.memcache_lock import memcache_lock, MemcacheLockException


def update_tags(tags, logger):
    for tag in tags:
        logger.info(u"TAG: {}".format(tag))
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
                                logger.info(u"TAG: {0} update count {1}".format(tag, cnt))
                                try:
                                    es_tag.update(roles=cnt)
                                except Exception as exc:
                                    logger.error(u"TAG: {0} failed to update {1}"
                                                 .format(tag, str(exc)).encode('utf-8').strip())
                                    raise
                            else:
                                logger.info(u"TAG: {0} no update required".format(tag).encode('utf-8').strip())
                        else:
                            logger.info("TAG: {} delete".format(tag).encode('utf-8').strip())
                            try:
                                es_tag.delete()
                            except Exception as exc:
                                logger.error(u"TAG: {0} failed to delete {1}"
                                             .format(tag, str(exc))
                                             .encode('utf-8').strip())
                                raise

                if not updated:
                    # new tag
                    try:
                        logger.info(u"TAG: {} add".format(tag).encode('utf-8').strip())
                        doc = TagDoc(tag=pg_tag.name, roles=cnt)
                        doc.meta.id = pg_tag.id
                        doc.save()
                    except Exception as exc:
                        logger.error(u"TAG: {0} failed to add {1}".format(tag, str(exc)).encode('utf-8').strip())
                        raise

        except MemcacheLockException as exc:
            logger.info(u"TAG: %s unable to get lock %s".format(tag, str(exc)).encode('utf-8').strip())


def update_platforms(platforms, logger):
    for platform in platforms:
        logger.info(u"PLATFORM: {}".format(platform).encode('utf-8').strip())
        platform_name = 'Enterprise_Linux' if platform == 'EL' else platform
        try:
            with memcache_lock("platform_%s" % platform):
                cnt = Role.objects.filter(active=True, is_valid=True, platforms__name=platform) \
                    .order_by('namespace', 'name') \
                    .distinct('namespace', 'name').count()
                es_platforms = PlatformDoc.search().query('match', name=platform_name).execute()
                updated = False

                for es_platform in es_platforms:
                    if es_platform.name == platform_name:
                        updated = True
                        if es_platform.roles != cnt:
                            logger.info(u"PLATFORM: {0} update count {1}".format(platform, cnt)
                                        .encode('utf-8').strip())
                            try:
                                es_platform.update(roles=cnt)
                            except Exception as exc:
                                logger.error("PLATFORM: {0} failed to update {1}"
                                             .format(platform, str(exc))
                                             .encode('utf-8').strip())
                                raise
                        else:
                            logger.info(u"PLATFORM: no update required {0}".format(platform).encode('utf-8').strip())

                if not updated:
                    # new platform
                    try:
                        logger.info(u"PLATFORM: {0} add".format(platform).encode('utf-8').strip())
                        releases = [p.release for p in Platform.objects.filter(active=True, name=platform)
                                    .order_by('release').distinct('release').all()]
                        doc = PlatformDoc(
                            name=platform_name,
                            releases=releases,
                            roles=cnt,
                        )
                        doc.save()
                    except Exception as exc:
                        logger.error(u"PLATFORM:{0} failed to add {1}".format(platform, str(exc)))
                        raise
        except MemcacheLockException as exc:
            logger.info(u"PLATFORM: %s failed to get lock %s".format(platform, str(exc)).encode('utf-8').strip())


def update_users(user, logger):
    logger.info(u"USER: {0}".format(user).encode('utf-8').strip())
    try:
        with memcache_lock("user_%s" % user):
            es_users = UserDoc.search().query('match', username=user).execute()
            updated = False

            for es_user in es_users:
                if es_user.username == user:
                    logger.info(u"USER: {0} already exists".format(user).encode('utf-8').strip())
                    updated = True

            if not updated:
                # new tag
                try:
                    logger.info(u"USER: {} add".format(user).encode('utf-8').strip())
                    doc = UserDoc(uername=user)
                    doc.save()
                except Exception as exc:
                    logger.error(u"USER: {0} failed to add {1}".format(user, str(exc)).encode('utf-8').strip())
                    raise
    except MemcacheLockException as exc:
        logger.info(u"USER: {0} failed to get lock {1}".format(user, str(exc)).encode('utf-8').strip())


@task(throws=(Exception,), name="galaxy.main.celerytasks.elastic_tasks.update_custom_indexes")
def update_custom_indexes(username=None, tags=[], platforms=[]):

    logger = update_custom_indexes.get_logger()

    if len(tags) > 0:
        update_tags(tags, logger)

    if len(platforms) > 0:
        update_platforms(platforms, logger)

    if username is not None:
        update_users(username, logger)
