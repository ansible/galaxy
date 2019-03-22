# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rolerating',
            name='code_quality',
        ),
        migrations.RemoveField(
            model_name='rolerating',
            name='documentation',
        ),
        migrations.RemoveField(
            model_name='rolerating',
            name='down_votes',
        ),
        migrations.RemoveField(
            model_name='rolerating',
            name='reliability',
        ),
        migrations.RemoveField(
            model_name='rolerating',
            name='up_votes',
        ),
        migrations.RemoveField(
            model_name='rolerating',
            name='wow_factor',
        ),
    ]
