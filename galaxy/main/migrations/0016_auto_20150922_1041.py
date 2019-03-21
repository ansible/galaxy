# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('main', '0015_auto_20150917_1504')]

    operations = [
        migrations.AddField(
            model_name='platform',
            name='alias',
            field=models.CharField(
                max_length=256,
                null=True,
                verbose_name='Search terms',
                blank=True,
            ),
        )
    ]
