# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20150826_0829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='average_score',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='role',
            name='num_ratings',
            field=models.IntegerField(default=0),
        ),
    ]
