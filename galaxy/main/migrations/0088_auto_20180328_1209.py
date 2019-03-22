from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0086_auto_20180328_1147'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='travis_build_url',
        ),
        migrations.RemoveField(
            model_name='content',
            name='travis_status_url',
        ),
    ]
