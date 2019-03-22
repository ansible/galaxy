from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0063_remove_deprecated_role_fields'),
    ]

    operations = [
        migrations.RenameModel('Role', 'Content'),
        migrations.RenameModel('RoleVersion', 'ContentVersion'),
        migrations.RenameField(
            model_name='contentversion',
            old_name='role',
            new_name='content',
        ),
    ]
