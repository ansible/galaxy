from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0119_scoring_edits_remove_contentrule'),
        ('accounts', '0007_auto_20180821_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='namespaces_followed',
            field=models.ManyToManyField(blank=True, to='main.Namespace'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='repositories_followed',
            field=models.ManyToManyField(blank=True, to='main.Repository'),
        ),
    ]
