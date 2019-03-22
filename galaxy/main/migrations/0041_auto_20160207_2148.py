# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0040_auto_20160206_0921'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together={('owner', 'github_user', 'github_repo')},
        ),
        migrations.AlterIndexTogether(
            name='repository',
            index_together=set(),
        )
    ]
