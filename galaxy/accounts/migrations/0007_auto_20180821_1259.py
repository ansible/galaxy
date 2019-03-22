from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_customuser_github_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='cache_refreshed',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='karma',
        ),
        migrations.AddField(
            model_name='customuser',
            name='notify_author_release',
            field=models.BooleanField(
                default=False,
                help_text=("Notify me when an author I'm following "
                           "creates new content.")),
        ),
        migrations.AddField(
            model_name='customuser',
            name='notify_content_release',
            field=models.BooleanField(
                default=False,
                help_text=("Notify me when a new release is available for "
                           "content I'm following.")),
        ),
        migrations.AddField(
            model_name='customuser',
            name='notify_galaxy_announce',
            field=models.BooleanField(
                default=False,
                help_text='Notify me when there is a Galaxy announcement'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='notify_import_fail',
            field=models.BooleanField(
                default=False,
                help_text='Notify me when an import fails.'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='notify_import_success',
            field=models.BooleanField(
                default=False,
                help_text='Notify me when an import succeeds.'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='notify_survey',
            field=models.BooleanField(
                default=False,
                help_text=("Notify me when a user adds a survey for "
                           "my content.")),
        ),
    ]
