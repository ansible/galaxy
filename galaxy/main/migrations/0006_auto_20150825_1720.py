# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20150824_1444'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='platform',
            index_together={('id', 'name')},
        ),
    ]
