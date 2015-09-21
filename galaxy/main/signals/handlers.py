from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, pre_save, pre_delete, post_save, post_delete
from django.contrib.auth import get_user_model

# elasticsearch
from elasticsearch_dsl import Search, Q

# local
from galaxy.main.models import Role, RoleRating, Tag
from galaxy.main.search_models import TagDoc, PlatformDoc
from galaxy.main.celerytasks.elastic_tasks import update_tags, update_platforms, update_users

User = get_user_model()

@receiver(post_save, sender=RoleRating)
@receiver(post_delete, sender=RoleRating)
def rolerating_post_save_handler(sender, **kwargs):
    role = Role.objects.get(pk=kwargs['instance'].role_id)
    cnt = 0.0
    total_score = 0.0
    for rating in role.ratings.all() :
        if rating.active:
            cnt += 1.0
            total_score += rating.score
    role.average_score = total_score / cnt if cnt > 0 else 0.0
    role.num_ratings = cnt
    role.save()


@receiver(pre_save, sender=Role)
def role_pre_save(sender, **kwargs):
    '''
    Before changes are made to a role grab the list of associated tags. The list will be used on post save 
    to signal celery to update elasticsearch indexes.
    '''
    instance = kwargs['instance']
    tags = instance.get_tags() if instance.id else []
    platforms = instance.get_unique_platforms() if instance.id else []
    username = instance.owner.username if instance.id else ''
    instance._saved_tag_names = tags
    instance._saved_username = username
    instance._saved_platforms = platforms


@receiver(post_save, sender=Role)
def role_post_save(sender, **kwargs):
    '''
    Signal celery to update the indexes.
    '''
    instance = kwargs['instance']
    tags = getattr(instance, '_saved_tag_names', None)
    if tags:
        for tag in tags:
            update_tags.delay(tag)

    username = getattr(instance, '_saved_username', None)
    if username:
        update_users.delay(username)

    platforms = getattr(instance, '_saved_platforms', None)
    if platforms:
        for platform in platforms:
            update_platforms.delay(platforms)

        