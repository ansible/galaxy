# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20150825_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rolerating',
            name='score',
            field=models.IntegerField(default=0, db_index=True),
        ),
    ]
