from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('accounts', '0002_auto_20150803_1328')]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='github_avatar',
            field=models.CharField(
                max_length=254, verbose_name='github avatar', blank=True
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='github_user',
            field=models.CharField(
                max_length=254, verbose_name='github user', blank=True
            ),
        ),
    ]
