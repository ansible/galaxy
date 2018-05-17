# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math

import django.contrib.postgres.fields
from django.conf import settings
from django.db import migrations
from django.db import models
from django.db import transaction
from django.db import IntegrityError
import django.db.models.deletion

from galaxy.api.aggregators import AvgWithZeroForNull
import galaxy.main.fields
import galaxy.main.mixins


# galaxy.main.migrations.0004_auto_20150824_1430
def round_score_up(apps, schema_editor):
    # Going forward each rating will contain a single score from 1 to 5.
    Ratings = apps.get_model("main", "RoleRating")
    for rating in Ratings.objects.all():
        rating.score = math.ceil(rating.score)
        rating.save()


# galaxy.main.migrations.0005_auto_20150824_1444
def update_roles(apps, schema_editor):
    # Going forward num_ratings and average_score will be stored on the role
    Roles = apps.get_model("main", "Role")
    for role in Roles.objects.all():
        role.num_ratings = role.ratings.filter(active=True).count()
        role.average_score = role.ratings.filter(active=True).aggregate(
            avg=AvgWithZeroForNull('score'))['avg'] or 0
        role.save()


# galaxy.main.migrations.0014_auto_20150917_1211
@transaction.atomic
def copy_categories_to_tags(apps, schema_editor):
    # tags will replace categories
    Categories = apps.get_model("main", "Category")
    Tag = apps.get_model("main", "Tag")
    for category in Categories.objects.all():
        for name in category.name.split(':'):
            try:
                with transaction.atomic():
                    tag = Tag(
                        name=name,
                        description=name,
                        active=True
                    )
                    tag.save()
            except IntegrityError:
                pass


@transaction.atomic
def copy_tags(apps, schema_editor):
    Roles = apps.get_model("main", "Role")
    Tags = apps.get_model("main", "Tag")
    for role in Roles.objects.all():
        for category in role.categories.all():
            for name in category.name.split(':'):
                if not role.tags.filter(name=name).exists():
                    t = Tags.objects.get(name=name)
                    role.tags.add(t)
                    role.save()


# galaxy.main.migrations.0018_auto_20151104_1701
@transaction.atomic
def set_namespace(apps, schema_editor):
    Roles = apps.get_model("main", "Role")
    for role in Roles.objects.all().order_by('github_user', 'name',
                                             '-modified'):
        try:
            with transaction.atomic():
                role.namespace = role.owner.username
                role.save()
        except Exception:
            pass


# galaxy.main.migrations.0055_contentblock
MAIN_TITLE_BLOCK = """
<h1><span class="ansible-color">Galaxy</span> is your hub for finding, 
reusing and sharing Ansible content</h1>
"""

MAIN_SHARE_BLOCK = """
<div class="share-icon"><i class="fa fa-share-alt fa-2x"></i></div>
<div class="info-label">Share</div>
<div class="content-txt">
   <p>Help other Ansible users by sharing the awesome roles you create.</p>
   <p>Maybe you have a role for installing and configuring a popular software
      package, or a role for deploying software built by your company. Whatever 
      it is, use Galaxy to share it with the community.</p>
   <p>Top content authors will be featured on the 
   <a href="/explore#">Explore page</a>, achieving worldwide fame! 
   Or at least fame on the internet among other developers and sysadmins.</p>
</div>

"""

MAIN_DOWNLOADS_BLOCK = """
<div class="download-icon"><i class="fa fa-cloud-download fa-2x"></i></div>

<div class="info-label">Download</div>
<div class="content-txt">

<p>Jump-start your automation project with great content from the Ansible
   community. Galaxy provides pre-packaged units of work known to Ansible 
   as <a href="http://docs.ansible.com/playbooks_roles.html#roles" 
       target="_blank">roles</a>.</p>
<p>Roles can be dropped into Ansible PlayBooks and immediately put to work. 
   You'll find roles for provisioning infrastructure, deploying 
   applications, and all of the tasks you do everyday.</p>

<p>Use <a href="/list#/roles">Search</a> to find roles for your project, 
   then download them onto your Ansible host using the
<a href="http://docs.ansible.com/ansible/galaxy.html#the-ansible-galaxy-command-line-tool" 
   target="_blank">ansible-galaxy</a> command that comes bundled 
   with Ansible.</p>
<p>For example:</p>
<pre>
$ ansible-galaxy install username.rolename
</pre>
</div>
"""

MAIN_FEATURED_BLOG_BLOCK = """
<span class="upcase title">BLOG:</span>
<a href="https://ansible.com/blog" target="_blank" class="blog-link">
Read the latest from The Inside Playbook, and keep up with what's happening 
in the Ansible universe.</a>
"""


def upgrade_contentblocks_data(apps, schema_editor):
    ContentBlock = apps.get_model("main", "ContentBlock")
    db_alias = schema_editor.connection.alias
    ContentBlock.objects.using(db_alias).bulk_create([
        ContentBlock(name='main-title', content=MAIN_TITLE_BLOCK),
        ContentBlock(name='main-share', content=MAIN_SHARE_BLOCK),
        ContentBlock(name='main-downloads', content=MAIN_DOWNLOADS_BLOCK),
        ContentBlock(name='main-featured-blog',
                     content=MAIN_FEATURED_BLOG_BLOCK),
    ])


# galaxy.main.migrations.0056_role_unique_repos
ROLE_DUPLICATES_QUERY = """
SELECT id FROM (
  SELECT
    id, ROW_NUMBER() OVER (
      PARTITION BY github_user, github_repo
      ORDER BY modified DESC) AS rnum
  FROM main_role) temp
WHERE temp.rnum > 1;
"""


def drop_role_duplicates(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Role = apps.get_model('main', 'Role')
    # NOTE(cutwater): All on_delete constraints in Django are software
    # defined, so we have to first query ids for deletion and then delete
    # Role objects with ORM.
    roles = Role.objects.using(db_alias).raw(ROLE_DUPLICATES_QUERY)
    for role in (
            Role.objects.using(db_alias)
                    .filter(pk__in=(r.id for r in roles))):
        # NOTE(cutwater): When calling .delete() on QuerySet, Django ORM
        # it seems that on_delete is not executed, so we have to execute
        # .delete() on each object specifically.
        role.delete()


class Migration(migrations.Migration):
    replaces = [
        (b'main', '0001_initial'),
        (b'main', '0002_auto_20150824_1342'),
        (b'main', '0003_auto_20150824_1354'),
        (b'main', '0004_auto_20150824_1430'),
        (b'main', '0005_auto_20150824_1444'),
        (b'main', '0006_auto_20150825_1720'),
        (b'main', '0007_auto_20150825_1723'),
        (b'main', '0008_auto_20150825_1737'),
        (b'main', '0009_auto_20150826_0829'),
        (b'main', '0010_auto_20150826_1017'),
        (b'main', '0014_auto_20150917_1211'),
        (b'main', '0015_auto_20150917_1504'),
        (b'main', '0016_auto_20150922_1041'),
        (b'main', '0017_auto_20151104_1700'),
        (b'main', '0018_auto_20151104_1701'),
        (b'main', '0019_auto_20151113_0936'),
        (b'main', '0020_auto_20151118_1350'),
        (b'main', '0021_auto_20151118_1425'),
        (b'main', '0022_auto_20151118_1642'),
        (b'main', '0023_auto_20151119_2020'),
        (b'main', '0024_importtask_finished'),
        (b'main', '0025_auto_20151120_1006'),
        (b'main', '0026_auto_20151122_0827'),
        (b'main', '0027_auto_20151125_0009'),
        (b'main', '0028_auto_20151125_1231'),
        (b'main', '0029_importtask_github_branch'),
        (b'main', '0030_auto_20151127_0824'),
        (b'main', '0031_auto_20151129_1230'),
        (b'main', '0032_role_download_count'),
        (b'main', '0033_refreshrolecount'),
        (b'main', '0034_auto_20151203_0014'),
        (b'main', '0035_remove_roleversion_release_date'),
        (b'main', '0036_auto_20151205_2254'),
        (b'main', '0037_roleversion_release_date'),
        (b'main', '0038_role_github_default_branch'),
        (b'main', '0039_namespace'),
        (b'main', '0040_auto_20160206_0921'),
        (b'main', '0041_auto_20160207_2148'),
        (b'main', '0042_auto_20160721_2318'),
        (b'main', '0043_role_role_type'),
        (b'main', '0044_auto_20160916_0839'),
        (b'main', '0045_role_commit_created'),
        (b'main', '0046_auto_20160930_1752'),
        (b'main', '0047_refreshrolecount_deleted'),
        (b'main', '0048_refreshrolecount_skipped'),
        (b'main', '0049_auto_20161013_1744'),
        (b'main', '0050_auto_20171024_0354'),
        (b'main', '0051_auto_20171108_2028'),
        (b'main', '0052_auto_20171108_2113'),
        (b'main', '0053_cloudplatform'),
        (b'main', '0054_role_type_demo'),
        (b'main', '0055_contentblock'),
        (b'main', '0056_role_unique_repos'),
        (b'main', '0057_stargazer_role_reference'),
        (b'main', '0058_stargazer_role_not_null'),
        (b'main', '0059_drop_role_rating')
    ]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('description',
                 galaxy.main.fields.TruncatingCharField(blank=True,
                                                        default=b'',
                                                        max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('name',
                 models.CharField(db_index=True, max_length=512, unique=True)),
                ('original_name', models.CharField(max_length=512)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('description',
                 galaxy.main.fields.TruncatingCharField(
                     blank=True, default=b'', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('name', models.CharField(db_index=True, max_length=512)),
                ('original_name', models.CharField(max_length=512)),
                ('release', models.CharField(
                    max_length=50,
                    verbose_name=b'Distribution Release Version')),
            ],
            options={
                'ordering': ['name', 'release'],
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('description',
                 galaxy.main.fields.TruncatingCharField(
                     blank=True, default=b'', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('name', models.CharField(db_index=True, max_length=512)),
                ('original_name', models.CharField(max_length=512)),
                ('github_user', models.CharField(
                    max_length=256, verbose_name=b'Github Username')),
                ('github_repo', models.CharField(
                    max_length=256, verbose_name=b'Github Repository')),
                ('readme', models.TextField(blank=True, default=b'')),
                ('min_ansible_version', models.CharField(
                    blank=True, max_length=10, null=True,
                    verbose_name=b'Minimum Ansible Version Required')),
                ('issue_tracker_url', models.CharField(
                    blank=True, max_length=256, null=True,
                    verbose_name=b'Issue Tracker URL')),
                ('license', models.CharField(
                    blank=True, max_length=30,
                    verbose_name=b'License (optional)')),
                ('company', models.CharField(
                    blank=True, max_length=50, null=True,
                    verbose_name=b'Company Name (optional)')),
                ('is_valid', models.BooleanField(
                    db_index=True, default=False)),
                ('featured', models.BooleanField(
                    default=False, editable=False)),
                ('bayesian_score', models.FloatField(
                    db_index=True, default=0.0, editable=False)),
                ('authors', models.ManyToManyField(
                    editable=False, related_name='author_on',
                    to=settings.AUTH_USER_MODEL)),
                ('categories', models.ManyToManyField(
                    blank=True, editable=False, help_text=b'',
                    related_name='roles', to=b'main.Category',
                    verbose_name=b'Categories')),
                ('dependencies', models.ManyToManyField(
                    blank=True, editable=False, related_name='+',
                    to=b'main.Role')),
                ('owner', models.ForeignKey(
                    editable=False,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='roles', to=settings.AUTH_USER_MODEL)),
                ('platforms', models.ManyToManyField(
                    blank=True, editable=False, help_text=b'',
                    related_name='roles', to=b'main.Platform',
                    verbose_name=b'Supported Platforms')),
            ],
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='RoleImport',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('description', galaxy.main.fields.TruncatingCharField(
                    blank=True, default=b'', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('celery_task_id', models.CharField(
                    blank=True, db_index=True, default=b'',
                    editable=False, max_length=100)),
                ('released', models.DateTimeField(auto_now_add=True)),
                ('state', models.CharField(
                    blank=True, db_index=True, default=b'', max_length=20)),
                ('status_message', models.CharField(
                    blank=True, default=b'', max_length=512)),
                ('role', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='imports',
                    to='main.Role')),
            ],
            options={
                'get_latest_by': 'released',
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='RoleRating',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('description', galaxy.main.fields.TruncatingCharField(
                    blank=True, default=b'', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('score', models.FloatField(
                    db_index=True, default=0.0, editable=False)),
                ('owner', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ratings',
                    to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ratings', to='main.Role')),
            ],
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='RoleVersion',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('description', galaxy.main.fields.TruncatingCharField(
                    blank=True, default=b'', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('name', models.CharField(db_index=True, max_length=512)),
                ('original_name', models.CharField(max_length=512)),
                ('release_date', models.DateTimeField(blank=True, null=True)),
                ('loose_version', galaxy.main.fields.LooseVersionField(
                    db_index=True, editable=False)),
                ('role', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='versions', to='main.Role')),
            ],
            options={
                'ordering': ('-loose_version',),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='UserAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('alias_name', models.CharField(max_length=30, unique=True)),
                ('alias_of', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='aliases',
                    to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'UserAliases',
            },
        ),
        migrations.AlterUniqueTogether(
            name='rolerating',
            unique_together={('owner', 'role')},
        ),
        migrations.AddField(
            model_name='role',
            name='average_score',
            field=models.FloatField(default=0.0, editable=False),
        ),
        migrations.AddField(
            model_name='role',
            name='num_ratings',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together={('owner', 'name')},
        ),
        migrations.RunPython(
            code=round_score_up,
        ),
        migrations.RunPython(
            code=update_roles,
        ),
        migrations.AlterIndexTogether(
            name='platform',
            index_together=set([]),
        ),
        migrations.AlterField(
            model_name='rolerating',
            name='score',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='role',
            name='average_score',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='role',
            name='num_ratings',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('description',
                 galaxy.main.fields.TruncatingCharField(blank=True,
                                                        default=b'',
                                                        max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('name',
                 models.CharField(db_index=True, max_length=512, unique=True)),
                ('original_name', models.CharField(max_length=512)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Tags',
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AddField(
            model_name='role',
            name='tags',
            field=models.ManyToManyField(
                blank=True, editable=False,
                related_name='tags', to=b'main.Tag',
                verbose_name=b'Tags'),
        ),
        migrations.RunPython(
            code=copy_categories_to_tags,
        ),
        migrations.RunPython(
            code=copy_tags,
        ),
        migrations.AlterField(
            model_name='role',
            name='categories',
            field=models.ManyToManyField(
                blank=True, editable=False,
                help_text=b'',
                related_name='categories',
                to=b'main.Category',
                verbose_name=b'Categories'),
        ),
        migrations.AlterField(
            model_name='role',
            name='tags',
            field=models.ManyToManyField(
                blank=True, editable=False,
                help_text=b'', related_name='roles',
                to=b'main.Tag', verbose_name=b'Tags'),
        ),
        migrations.AddField(
            model_name='platform',
            name='alias',
            field=models.CharField(
                blank=True, max_length=256, null=True,
                verbose_name=b'Search terms'),
        ),
        migrations.RemoveField(
            model_name='role',
            name='authors',
        ),
        migrations.AddField(
            model_name='role',
            name='namespace',
            field=models.CharField(
                blank=True, max_length=256, null=True,
                verbose_name=b'Namespace'),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together={('namespace', 'name')},
        ),
        migrations.RunPython(
            code=set_namespace,
        ),
        migrations.CreateModel(
            name='ImportTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('description',
                 galaxy.main.fields.TruncatingCharField(blank=True,
                                                        default=b'',
                                                        max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('github_user', models.CharField(
                    max_length=256, verbose_name=b'Github Username')),
                ('github_repo', models.CharField(
                    max_length=256, verbose_name=b'Github Repository')),
                ('github_reference', models.CharField(
                    max_length=256, verbose_name=b'Github Reference')),
                ('alternate_role_name', models.CharField(
                    blank=True, max_length=256, null=True,
                    verbose_name=b'Alternate Role Name')),
                ('celery_task_id',
                 models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(default=b'PENDING', max_length=20)),
                ('started', models.DateTimeField(blank=True, null=True)),
                ('owner', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='import_tasks',
                    to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='import_tasks',
                    to='main.Role')),
            ],
            options={
                'ordering': ('-id',),
                'get_latest_by': 'created',
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='ImportTaskMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('description',
                 galaxy.main.fields.TruncatingCharField(blank=True,
                                                        default=b'',
                                                        max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('message_type', models.CharField(max_length=10)),
                ('message_text', models.CharField(max_length=256)),
                ('task', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='messages',
                    to='main.ImportTask')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('description', galaxy.main.fields.TruncatingCharField(
                    blank=True, default=b'', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('source', models.CharField(
                    editable=False, max_length=20, verbose_name=b'Source')),
                ('owner', models.ForeignKey(
                    editable=False,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notifications',
                    to=settings.AUTH_USER_MODEL)),
                ('roles', models.ManyToManyField(
                    editable=False,
                    related_name='notifications',
                    to=b'main.Role',
                    verbose_name=b'Roles')),
                ('imports', models.ManyToManyField(
                    editable=False,
                    related_name='notifications',
                    to=b'main.ImportTask',
                    verbose_name=b'Tasks')),
                ('github_branch', models.CharField(
                    blank=True, editable=False, max_length=256,
                    verbose_name=b'GitHub Branch')),
                ('messages', django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=256), default=list,
                    editable=False, size=None)),
                ('commit', models.CharField(blank=True, max_length=256)),
                ('commit_message',
                 models.CharField(blank=True, max_length=256)),
                ('committed_at', models.DateTimeField(null=True)),
                ('travis_build_url',
                 models.CharField(blank=True, max_length=256)),
                (
                    'travis_status',
                    models.CharField(blank=True, max_length=256)),
            ],
            options={
                'ordering': ('-id',),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='NotificationSecret',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('description', galaxy.main.fields.TruncatingCharField(
                    blank=True, default=b'', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('source', models.CharField(
                    max_length=20, verbose_name=b'Source')),
                ('secret', models.CharField(
                    db_index=True, max_length=256, verbose_name=b'Secret')),
                ('owner', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notification_secrets',
                    to=settings.AUTH_USER_MODEL)),
                ('github_repo', models.CharField(
                    max_length=256, verbose_name=b'Github Repository')),
                ('github_user', models.CharField(
                    max_length=256, verbose_name=b'Github Username')),
            ],
            options={
                'ordering': ('source', 'github_user', 'github_repo'),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AlterUniqueTogether(
            name='notificationsecret',
            unique_together={('source', 'github_user', 'github_repo')},
        ),
        migrations.AlterModelOptions(
            name='role',
            options={'ordering': ['namespace', 'name']},
        ),
        migrations.AlterField(
            model_name='role',
            name='is_valid',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='role',
            name='license',
            field=models.CharField(
                blank=True, max_length=50, verbose_name=b'License (optional)'),
        ),
        migrations.RemoveField(
            model_name='roleimport',
            name='role',
        ),
        migrations.RemoveField(
            model_name='role',
            name='owner',
        ),
        migrations.AddField(
            model_name='role',
            name='github_branch',
            field=models.CharField(
                blank=True, default=b'', max_length=256,
                verbose_name=b'Github Branch'),
        ),
        migrations.DeleteModel(
            name='RoleImport',
        ),
        migrations.AddField(
            model_name='role',
            name='travis_status_url',
            field=models.CharField(
                blank=True, default=b'', max_length=256,
                verbose_name=b'Travis Build Status'),
        ),
        migrations.AddField(
            model_name='role',
            name='forks_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='role',
            name='open_issues_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='role',
            name='stargazers_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='role',
            name='watchers_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='role',
            name='commit',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='role',
            name='commit_message',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='importtask',
            name='finished',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='role',
            name='commit_url',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('description', galaxy.main.fields.TruncatingCharField(
                    blank=True, default=b'', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('github_user', models.CharField(
                    max_length=256, verbose_name=b'Github Username')),
                ('github_repo', models.CharField(
                    max_length=256, verbose_name=b'Github Repository')),
                ('is_enabled', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(
                    editable=False,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='repositories',
                    to=settings.AUTH_USER_MODEL)),
            ],
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AlterField(
            model_name='role',
            name='bayesian_score',
            field=models.FloatField(default=0.0, editable=False),
        ),
        migrations.AlterIndexTogether(
            name='repository',
            index_together={
                ('owner', 'github_user', 'github_repo', 'is_enabled')
            },
        ),
        migrations.AlterModelOptions(
            name='repository',
            options={'ordering': ('github_user', 'github_repo')},
        ),
        migrations.AddField(
            model_name='role',
            name='imported',
            field=models.DateTimeField(null=True, verbose_name=b'Last Import'),
        ),
        migrations.AlterIndexTogether(
            name='repository',
            index_together={
                ('github_user', 'github_repo'),
                ('owner', 'github_user', 'github_repo', 'is_enabled')
            },
        ),
        migrations.AddField(
            model_name='importtask',
            name='commit',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='importtask',
            name='commit_message',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='importtask',
            name='commit_url',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='importtask',
            name='forks_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='importtask',
            name='open_issues_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='importtask',
            name='stargazers_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='importtask',
            name='watchers_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='importtask',
            name='github_branch',
            field=models.CharField(
                blank=True, default=b'', max_length=256,
                verbose_name=b'Github Branch'),
        ),
        migrations.CreateModel(
            name='Stargazer',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('description', galaxy.main.fields.TruncatingCharField(
                    blank=True, default=b'', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('github_user', models.CharField(
                    max_length=256, verbose_name=b'Github Username')),
                ('github_repo', models.CharField(
                    max_length=256, verbose_name=b'Github Repository')),
                ('owner', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='starred',
                    to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('owner', 'github_user', 'github_repo'),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('description', galaxy.main.fields.TruncatingCharField(
                    blank=True, default=b'', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('github_user', models.CharField(
                    max_length=256, verbose_name=b'Github Username')),
                ('github_repo', models.CharField(
                    max_length=256, verbose_name=b'Github Repository')),
                ('owner', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='subscriptions',
                    to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('owner', 'github_user', 'github_repo'),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AlterIndexTogether(
            name='subscription',
            index_together={('owner', 'github_user', 'github_repo')},
        ),
        migrations.AlterIndexTogether(
            name='stargazer',
            index_together={('owner', 'github_user', 'github_repo')},
        ),
        migrations.AlterField(
            model_name='repository',
            name='owner',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='repositories', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='stargazer',
            unique_together={('owner', 'github_user', 'github_repo')},
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together={('owner', 'github_user', 'github_repo')},
        ),
        migrations.AlterIndexTogether(
            name='stargazer',
            index_together=set([]),
        ),
        migrations.AlterIndexTogether(
            name='subscription',
            index_together=set([]),
        ),
        migrations.AddField(
            model_name='role',
            name='download_count',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='RefreshRoleCount',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('description', galaxy.main.fields.TruncatingCharField(
                    blank=True, default=b'', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('state', models.CharField(max_length=20)),
                ('failed', models.IntegerField(default=0, null=True)),
                ('passed', models.IntegerField(default=0, null=True)),
                ('deleted', models.IntegerField(default=0, null=True)),
                ('updated', models.IntegerField(default=0, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.RemoveField(
            model_name='roleversion',
            name='release_date',
        ),
        migrations.AddField(
            model_name='importtask',
            name='travis_build_url',
            field=models.CharField(
                blank=True, default=b'', max_length=256,
                verbose_name=b'Travis Build URL'),
        ),
        migrations.AddField(
            model_name='importtask',
            name='travis_status_url',
            field=models.CharField(
                blank=True, default=b'', max_length=256,
                verbose_name=b'Travis Build Status'),
        ),
        migrations.AddField(
            model_name='role',
            name='travis_build_url',
            field=models.CharField(
                blank=True, default=b'', max_length=256,
                verbose_name=b'Travis Build URL'),
        ),
        migrations.AlterField(
            model_name='importtask',
            name='github_reference',
            field=models.CharField(
                blank=True, default=b'', max_length=256,
                null=True, verbose_name=b'Github Reference'),
        ),
        migrations.AddField(
            model_name='roleversion',
            name='release_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='role',
            name='github_default_branch',
            field=models.CharField(
                default=b'master', max_length=256,
                verbose_name=b'Default Branch'),
        ),
        migrations.CreateModel(
            name='Namespace',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('description', galaxy.main.fields.TruncatingCharField(
                    blank=True, default=b'', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('namespace', models.CharField(
                    max_length=256, unique=True,
                    verbose_name=b'GitHub namespace')),
                ('name', models.CharField(
                    blank=True, max_length=256, null=True,
                    verbose_name=b'GitHub name')),
                ('avatar_url', models.CharField(
                    blank=True, max_length=256, null=True,
                    verbose_name=b'GitHub Avatar URL')),
                ('location', models.CharField(
                    blank=True, max_length=256, null=True,
                    verbose_name=b'Location')),
                ('company', models.CharField(
                    blank=True, max_length=256, null=True,
                    verbose_name=b'Location')),
                ('email', models.CharField(
                    blank=True, max_length=256, null=True,
                    verbose_name=b'Location')),
                ('html_url', models.CharField(
                    blank=True, max_length=256, null=True,
                    verbose_name=b'URL')),
                ('followers', models.IntegerField(
                    null=True, verbose_name=b'Followers')),
            ],
            options={
                'ordering': ('namespace',),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AddField(
            model_name='role',
            name='readme_type',
            field=models.CharField(
                max_length=5, null=True, verbose_name=b'README type'),
        ),
        migrations.AlterField(
            model_name='role',
            name='readme',
            field=models.TextField(
                blank=True, default=b'', verbose_name=b'README content'),
        ),
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together={('owner', 'github_user', 'github_repo')},
        ),
        migrations.AlterIndexTogether(
            name='repository',
            index_together=set(),
        ),
        migrations.AddField(
            model_name='role',
            name='readme_html',
            field=models.TextField(
                blank=True, default=b'', verbose_name=b'README HTML'),
        ),
        migrations.AlterField(
            model_name='role',
            name='readme',
            field=models.TextField(
                blank=True, default=b'', verbose_name=b'README raw content'),
        ),
        migrations.AddField(
            model_name='role',
            name='role_type',
            field=models.CharField(
                choices=[
                    (b'ANS', b'Ansible'),
                    (b'CON', b'Container Enabled'),
                    (b'APP', b'Container App'),
                    (b'DEM', b'Demo')],
                default=b'ANS', editable=False, max_length=3),
        ),
        migrations.AddField(
            model_name='role',
            name='container_yml',
            field=models.TextField(
                blank=True, null=True, verbose_name=b'container.yml'),
        ),
        migrations.AddField(
            model_name='role',
            name='commit_created',
            field=models.DateTimeField(
                null=True, verbose_name=b'Laste Commit DateTime'),
        ),
        migrations.AddField(
            model_name='role',
            name='min_ansible_container_version',
            field=models.CharField(
                blank=True, max_length=10, null=True,
                verbose_name=b'Min Ansible Container Version'),
        ),
        migrations.AlterField(
            model_name='role',
            name='min_ansible_version',
            field=models.CharField(
                blank=True, max_length=10, null=True,
                verbose_name=b'Min Ansible Version'),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    blank=True, default=b'', max_length=255)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('url', models.CharField(help_text=b'', max_length=256)),
                ('role', models.ForeignKey(
                    help_text=b'', null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='videos',
                    to='main.Role')),
            ],
            options={
                'verbose_name': 'videos',
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='CloudPlatform',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    blank=True, default=b'', max_length=255)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('name', models.CharField(
                    db_index=True, max_length=512, unique=True)),
                ('original_name', models.CharField(max_length=512)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AddField(
            model_name='role',
            name='cloud_platforms',
            field=models.ManyToManyField(
                blank=True, editable=False, related_name='roles',
                to=b'main.CloudPlatform', verbose_name=b'Cloud Platforms'),
        ),
        migrations.CreateModel(
            name='ContentBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.SlugField(unique=True)),
                ('content',
                 models.TextField(blank=True, verbose_name=b'content')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.RunPython(
            code=upgrade_contentblocks_data,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunSQL(
            sql='SET CONSTRAINTS ALL IMMEDIATE',
            reverse_sql='',
        ),
        migrations.RunPython(
            code=drop_role_duplicates,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together={
                ('github_user', 'github_repo'),
                ('namespace', 'name')
            },
        ),
        migrations.RunSQL(
            sql='',
            reverse_sql='SET CONSTRAINTS ALL IMMEDIATE',
        ),
        migrations.AlterModelOptions(
            name='stargazer',
            options={},
        ),
        migrations.AddField(
            model_name='stargazer',
            name='role',
            field=models.ForeignKey(
                default=None, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='main.Role'),
        ),
        migrations.AlterField(
            model_name='stargazer',
            name='github_user',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='stargazer',
            name='github_repo',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.RunSQL(
            sql="""
                UPDATE main_stargazer
                SET 
                  role_id = main_role.id
                FROM main_role
                WHERE main_stargazer.github_user = main_role.github_user
                  AND main_stargazer.github_repo = main_role.github_repo 
            """,
            reverse_sql="""
                UPDATE main_stargazer
                SET 
                  github_user = main_role.github_user,
                  github_repo = main_role.github_repo
                FROM main_role
                WHERE main_stargazer.role_id = main_role.id 
            """,
        ),
        migrations.RunSQL(
            sql='DELETE FROM main_stargazer WHERE role_id IS NULL',
            reverse_sql='',
        ),
        migrations.AlterField(
            model_name='stargazer',
            name='role',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='main.Role'),
        ),
        migrations.RemoveField(
            model_name='stargazer',
            name='github_repo',
        ),
        migrations.RemoveField(
            model_name='stargazer',
            name='github_user',
        ),
        migrations.AlterUniqueTogether(
            name='stargazer',
            unique_together={('owner', 'role')},
        ),
        migrations.AlterField(
            model_name='stargazer',
            name='role',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='stars', to='main.Role'),
        ),
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
