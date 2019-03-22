# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_importtask_finished'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='commit_url',
            field=models.CharField(max_length=256, blank=True),
        ),
    ]
