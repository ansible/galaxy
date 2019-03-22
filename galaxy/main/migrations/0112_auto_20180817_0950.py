from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import galaxy.main.mixins


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0111_repository_deprecated'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunitySurvey',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('docs', models.IntegerField(
                    null=True,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(5)
                    ]
                )),
                ('ease_of_use', models.IntegerField(
                    null=True,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(5)
                    ]
                )),
                ('does_what_it_says', models.IntegerField(
                    null=True,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(5)
                    ]
                )),
                ('works_as_is', models.IntegerField(
                    null=True,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(5)
                    ]
                )),
                ('used_in_production', models.IntegerField(
                    null=True,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(5)
                    ]
                )),
                ('repository', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='main.Repository'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AlterUniqueTogether(
            name='communitysurvey',
            unique_together={('user', 'repository')},
        ),
    ]
