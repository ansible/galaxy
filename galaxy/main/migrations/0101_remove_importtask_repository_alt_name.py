from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0100_notifications'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='importtask',
            name='repository_alt_name',
        ),
    ]
