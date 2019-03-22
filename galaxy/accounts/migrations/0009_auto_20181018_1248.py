from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20181011_1056'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='namespaces_followed',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='notify_author_release',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='notify_content_release',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='notify_galaxy_announce',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='notify_import_fail',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='notify_import_success',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='notify_survey',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='repositories_followed',
        ),
    ]
