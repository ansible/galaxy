# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_refreshrolecount'),
    ]

    operations = [
        migrations.AddField(
            model_name='refreshrolecount',
            name='failed',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='refreshrolecount',
            name='passed',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
