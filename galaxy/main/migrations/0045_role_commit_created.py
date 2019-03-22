# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('main', '0044_auto_20160916_0839')]

    operations = [
        migrations.AddField(
            model_name='role',
            name='commit_created',
            field=models.DateTimeField(
                null=True, verbose_name='Laste Commit DateTime'
            ),
        )
    ]
