from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

# elasticsearch
from elasticsearch_dsl import Search, Q

# local
from galaxy.main.models import Role, RoleRating
from galaxy.main.search_models import TagDoc, PlatformDoc


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


# @receiver(post_save, sender=Role)
# @receiver(post_delete, sender=Role)
# def role_post_save_handler(sender, **kwargs):
#     role = Role.objects.get(pk=kwargs['instance'].role_id)
#     if role.tags:
#         for tag in role.tags:
#             stored_tags = TagDoc.search().query('match', tag=tag).execute()
#             for stored_tag in stored_tags:
#                 if stored_tag.tag == tag:
                    


                
