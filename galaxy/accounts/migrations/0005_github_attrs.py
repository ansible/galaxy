from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_customuser_cache_refreshed'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='github_avatar',
            new_name='avatar_url',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='avatar_url',
            field=models.CharField(blank=True, max_length=256,
                                   verbose_name='avatar URL'),
        ),
    ]
