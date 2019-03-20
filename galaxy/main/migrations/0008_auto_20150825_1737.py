# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20150825_1723'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='platform',
            index_together=set([]),
        ),
    ]
