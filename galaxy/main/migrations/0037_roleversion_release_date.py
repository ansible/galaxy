# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_auto_20151205_2254'),
    ]

    operations = [
        migrations.AddField(
            model_name='roleversion',
            name='release_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
