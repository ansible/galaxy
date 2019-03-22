from django.db import migrations, models
import galaxy.main.mixins
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0117_namespace_search_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfluxSessionIdentifier',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('session_id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False
                )),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
    ]
