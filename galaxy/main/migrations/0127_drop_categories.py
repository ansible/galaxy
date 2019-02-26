from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0126_notification_commit_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='categories',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]
