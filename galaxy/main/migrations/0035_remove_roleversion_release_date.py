# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_auto_20151203_0014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roleversion',
            name='release_date',
        ),
    ]
