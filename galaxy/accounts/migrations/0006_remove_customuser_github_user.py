from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_github_attrs'),
        ('main', '0090_issue_tracker_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='github_user',
        ),
    ]
