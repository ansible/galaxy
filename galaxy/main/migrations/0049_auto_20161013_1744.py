# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0048_refreshrolecount_skipped'),
    ]

    operations = [
        migrations.RenameField(
            model_name='refreshrolecount',
            old_name='skipped',
            new_name='updated',
        ),
    ]
