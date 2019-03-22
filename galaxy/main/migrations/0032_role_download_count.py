# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_auto_20151129_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='download_count',
            field=models.IntegerField(default=0),
        ),
    ]
