from django.db import migrations
import galaxy.main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0125_community_score_question_average'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='commit_message',
            field=galaxy.main.fields.TruncatingCharField(
                blank=True,
                default='',
                max_length=256),
        ),
    ]
