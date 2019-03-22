from django.db import models, migrations

import galaxy.main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0076_content_namespace_ref'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='content',
            options={'ordering': ['namespace', 'content_type', 'name']},
        ),
        migrations.AddField(
            model_name='repository',
            name='description',
            field=galaxy.main.fields.TruncatingCharField(
                default='', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='repository',
            name='commit_created',
            field=models.DateTimeField(null=True,
                                       verbose_name='Last Commit DateTime'),
        ),
    ]
