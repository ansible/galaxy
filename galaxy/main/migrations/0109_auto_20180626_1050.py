from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('main', '0108_sanitize_namespace_names')]

    operations = [
        migrations.AlterModelOptions(
            name='content',
            options={
                'ordering': ['namespace', 'repository', 'name', 'content_type']
            },
        ),
        migrations.AlterModelOptions(name='repositoryversion', options={}),
        migrations.AlterUniqueTogether(
            name='content',
            unique_together={
                ('namespace', 'repository', 'name', 'content_type')
            },
        ),
    ]
