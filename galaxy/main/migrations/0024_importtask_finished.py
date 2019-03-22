# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_auto_20151119_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='importtask',
            name='finished',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
