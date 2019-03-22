from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0119_scoring_edits_remove_contentrule'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='quality_score_date',
            field=models.DateTimeField(null=True,
                                       verbose_name='DateTime last scored'),
        ),
    ]
