# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import models, migrations
import galaxy.main.fields
import galaxy.main.mixins


class Migration(migrations.Migration):

    dependencies = [('main', '0032_role_download_count')]

    operations = [
        migrations.CreateModel(
            name='RefreshRoleCount',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'description',
                    galaxy.main.fields.TruncatingCharField(
                        default='', max_length=255, blank=True
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('state', models.CharField(max_length=20)),
            ],
            options={'abstract': False},
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        )
    ]
