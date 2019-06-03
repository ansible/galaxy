from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', 'v2_4_0'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='rolerating',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='rolerating',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='rolerating',
            name='role',
        ),
        migrations.DeleteModel(
            name='RoleRating',
        ),
    ]
