# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import migrations

from galaxy.api.aggregators import AvgWithZeroForNull


def update_roles(apps, schema_editor):
    # Going forward num_ratings and average_score
    # will be stored on the role
    db_alias = schema_editor.connection.alias
    Roles = apps.get_model("main", "Role")
    for role in Roles.objects.using(db_alias).all():
        role.num_ratings = role.ratings.filter(active=True).count()
        role.average_score = (
                role.ratings.filter(active=True).aggregate(
                    avg=AvgWithZeroForNull('score')
                )['avg']
                or 0
        )
        role.save()


class Migration(migrations.Migration):

    dependencies = [('main', '0004_auto_20150824_1430')]

    operations = [migrations.RunPython(update_roles)]
