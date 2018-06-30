# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

import galaxy.main.mixins
import galaxy.main.fields


COPY_NAMESPACE_DATA = """
INSERT INTO main_providernamespace (
  description, created, modified, active, name, display_name,
  avatar_url, location, company, email, html_url, followers)
SELECT
  description, created, modified, active, a.namespace, name,
  avatar_url, location, company, email, html_url, followers
FROM main_namespace as a INNER JOIN
  (SELECT namespace, min(id) as id
   FROM main_namespace
   GROUP BY namespace) as b ON a.namespace = b.namespace and a.id = b.id
"""

ADD_REPO_GITHUB_USERS = """
INSERT INTO main_providernamespace
  (created, modified, active, name, description)
SELECT created, modified, true, b.github_user, b.github_user
FROM main_repository as a INNER JOIN
  (SELECT github_user, min(id) as id
   FROM main_repository
   GROUP BY github_user) as b
   ON a.github_user = b.github_user and a.id = b.id
WHERE a.github_user not in (
  SELECT name FROM main_providernamespace WHERE name = a.github_user)
"""

ADD_ROLE_NAMESPACE = """
INSERT INTO main_providernamespace
  (created, modified, active, name, description)
SELECT
  created, modified, true, a.namespace, a.namespace
FROM main_content as a INNER JOIN
  (SELECT namespace, min(id) as id
   FROM main_content
   GROUP BY namespace) as b ON a.namespace = b.namespace and a.id = b.id
WHERE a.namespace not in (
  SELECT name FROM main_providernamespace WHERE name = a.namespace)
"""

NAMESPACE_FROM_PROVIDER_NAMESPACE = """
INSERT INTO main_namespace (
  name, description, created, modified, active, original_name,
  avatar_url, location, company, email, html_url
)
SELECT
  a.name, description, created, modified, true, a.name,
  avatar_url, location, company, email, html_url
FROM main_providernamespace as a INNER JOIN
  (SELECT name, min(id) as id
   FROM main_providernamespace
   GROUP BY name) as b ON a.name = b.name and a.id = b.id
"""

SET_PROVIDER_NAMESPACE_FK = """
UPDATE main_providernamespace
SET
provider_id = (
  SELECT id
  FROM main_provider
  WHERE name = 'GitHub'
),
namespace_id = (
  SELECT id
  FROM main_namespace
  WHERE main_namespace.name = main_providernamespace.name
)
"""

ADD_NAMESPACE_OWNERS = """
INSERT INTO main_namespace_owners
( customuser_id, namespace_id)
SELECT u.id, n.id
FROM accounts_customuser as u, main_namespace as n
WHERE u.github_user = n.name
"""

ADD_GITHUB_PROVIDER = """
INSERT INTO main_provider
  (created, modified, description, name, original_name, active)
VALUES
  (CURRENT_DATE, CURRENT_DATE, 'Public GitHub', 'GitHub', 'GitHub', true)
"""

ADD_MISSING_OWNERS = """
INSERT INTO main_namespace_owners (
  namespace_id,
  customuser_id
)
SELECT DISTINCT
  a.namespace_id,
  a.customuser_id
FROM (
  SELECT
    c.id AS namespace_id,
    a.customuser_id AS customuser_id
  FROM
    main_repository_owners a,
    main_repository b,
    main_namespace c
  WHERE
    a.repository_id = b.id
    AND b.github_user = c.name
) AS a
LEFT JOIN main_namespace_owners AS b
    ON a.namespace_id = b.namespace_id
    AND a.customuser_id = b.customuser_id
WHERE b.namespace_id IS NULL
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0064_rename_role'),
        ('accounts', '0003_auto_20151125_0840'),
    ]

    operations = [

        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True,
                    primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default=b'', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(
                    unique=True, max_length=512, db_index=True)),
                ('original_name', models.CharField(max_length=512)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),

        migrations.CreateModel(
            name='ProviderNamespace',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True,
                    primary_key=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default=b'', max_length=255, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(
                    max_length=256, verbose_name=b'Name')),
                ('display_name', models.CharField(
                    verbose_name=b'Display Name', max_length=256,
                    null=True, editable=False, blank=True)),
                ('avatar_url', models.CharField(
                    verbose_name=b'Avatar URL', max_length=256,
                    null=True, editable=False, blank=True)),
                ('location', models.CharField(
                    verbose_name=b'Location', max_length=256,
                    null=True, editable=False, blank=True)),
                ('company', models.CharField(
                    verbose_name=b'Company Name', max_length=256,
                    null=True, editable=False, blank=True)),
                ('email', models.CharField(
                    verbose_name=b'Email Address', max_length=256,
                    null=True, editable=False, blank=True)),
                ('html_url', models.CharField(
                    verbose_name=b'Web Site URL', max_length=256,
                    null=True, editable=False, blank=True)),
                ('followers', models.IntegerField(
                    null=True, editable=False,
                    verbose_name="Followers")),
                ('namespace', models.ForeignKey(
                    related_name='namespaces', editable=False,
                    to='main.Namespace', null=True,
                    verbose_name=b'Namespace')),
                ('provider', models.ForeignKey(
                    related_name='provider', verbose_name=b'Provider',
                    to='main.Provider', null=True)),
            ],
            options={
                'ordering': ('provider', 'name',),
                'unique_together': {('provider', 'name'),
                                    ('namespace', 'provider', 'name')},
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),

        migrations.RunSQL(
            sql=COPY_NAMESPACE_DATA,
            reverse_sql=migrations.RunSQL.noop
        ),

        migrations.DeleteModel(
            name='Namespace',
        ),

        migrations.CreateModel(
            name='Namespace',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default=b'', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(
                    unique=True, max_length=512, db_index=True)),
                ('original_name', models.CharField(max_length=512)),
                ('avatar_url', models.CharField(
                    max_length=256, null=True,
                    verbose_name=b'Avatar URL', blank=True)),
                ('location', models.CharField(
                    max_length=256, null=True,
                    verbose_name=b'Location', blank=True)),
                ('company', models.CharField(
                    max_length=256, null=True,
                    verbose_name=b'Company Name', blank=True)),
                ('email', models.CharField(
                    max_length=256, null=True,
                    verbose_name=b'Email Address', blank=True)),
                ('html_url', models.CharField(
                    max_length=256, null=True,
                    verbose_name=b'Web Site URL', blank=True)),
                ('owners', models.ManyToManyField(
                    related_name='namespaces', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),

        migrations.RunSQL(sql=(
            ADD_GITHUB_PROVIDER,
            ADD_REPO_GITHUB_USERS,
            ADD_ROLE_NAMESPACE,
            NAMESPACE_FROM_PROVIDER_NAMESPACE,
            SET_PROVIDER_NAMESPACE_FK,
            ADD_NAMESPACE_OWNERS,
            ADD_MISSING_OWNERS,
        )),
    ]
