# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import models, migrations
import galaxy.main.mixins
from django.conf import settings
import galaxy.main.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0029_importtask_github_branch'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stargazer',
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
                (
                    'github_user',
                    models.CharField(
                        max_length=256, verbose_name='Github Username'
                    ),
                ),
                (
                    'github_repo',
                    models.CharField(
                        max_length=256, verbose_name='Github Repository'
                    ),
                ),
                (
                    'owner',
                    models.ForeignKey(
                        related_name='starred',
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={'ordering': ('owner', 'github_user', 'github_repo')},
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Subscription',
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
                (
                    'github_user',
                    models.CharField(
                        max_length=256, verbose_name='Github Username'
                    ),
                ),
                (
                    'github_repo',
                    models.CharField(
                        max_length=256, verbose_name='Github Repository'
                    ),
                ),
                (
                    'owner',
                    models.ForeignKey(
                        related_name='subscriptions',
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={'ordering': ('owner', 'github_user', 'github_repo')},
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AlterIndexTogether(
            name='subscription',
            index_together={('owner', 'github_user', 'github_repo')},
        ),
        migrations.AlterIndexTogether(
            name='stargazer',
            index_together={('owner', 'github_user', 'github_repo')},
        ),
    ]
