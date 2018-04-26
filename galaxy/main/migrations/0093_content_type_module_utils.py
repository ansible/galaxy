# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import galaxy.main.mixins
from django.utils.timezone import utc
import galaxy.main.fields

UPGRADE_INSERT_CONTENT_TYPES = """
INSERT INTO main_contenttype 
  (name, description, created, modified)
VALUES
    ('module_utils', 'Module Utils', now(), now())
"""

DOWNGRADE_CONTENT_TYPES = """
DELETE FROM main_contenttype
  WHERE name = 'module_utils'
  (name, description, created, modified)
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0092_content_module_utils'),
    ]

    operations = [
        migrations.RunSQL(sql=UPGRADE_INSERT_CONTENT_TYPES,
                          reverse_sql=DOWNGRADE_CONTENT_TYPES),
    ]
