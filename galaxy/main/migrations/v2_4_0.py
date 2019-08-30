from django.conf import settings
import django.contrib.postgres.fields
from django.db import models
from django.db import migrations

import galaxy.main.mixins
import galaxy.main.fields

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
"""  # noqa: E501

MAIN_FEATURED_BLOG_BLOCK = """
<span class="upcase title">BLOG:</span>
<a href="https://ansible.com/blog" target="_blank" class="blog-link">
Read the latest from The Inside Playbook, and keep up with what's happening
in the Ansible universe.</a>
"""


def upgrade_contentblocks_data(apps, schema_editor):
    ContentBlock = apps.get_model("main", "ContentBlock")
    db_alias = schema_editor.connection.alias
    ContentBlock.objects.using(db_alias).bulk_create(
        [
            ContentBlock(name='main-title', content=MAIN_TITLE_BLOCK),
            ContentBlock(name='main-share', content=MAIN_SHARE_BLOCK),
            ContentBlock(name='main-downloads', content=MAIN_DOWNLOADS_BLOCK),
            ContentBlock(
                name='main-featured-blog', content=MAIN_FEATURED_BLOG_BLOCK
            ),
        ]
    )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(
                    unique=True, max_length=512, db_index=True)),
                ('original_name', models.CharField(max_length=512)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='CloudPlatform',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(
                    unique=True, max_length=512, db_index=True)),
                ('original_name', models.CharField(max_length=512)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='ContentBlock',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.SlugField(unique=True)),
                ('content', models.TextField(
                    verbose_name='content', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='ImportTask',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(
                    default=True, db_index=True)),
                ('github_user', models.CharField(
                    max_length=256, verbose_name='Github Username')),
                ('github_repo', models.CharField(
                    max_length=256, verbose_name='Github Repository')),
                ('github_reference', models.CharField(
                    default='', max_length=256, null=True,
                    verbose_name='Github Reference', blank=True)),
                ('alternate_role_name', models.CharField(
                    max_length=256, null=True, blank=True,
                    verbose_name='Alternate Role Name')),
                ('celery_task_id', models.CharField(
                    max_length=100, null=True, blank=True)),
                ('state', models.CharField(default='PENDING', max_length=20)),
                ('started', models.DateTimeField(null=True, blank=True)),
                ('finished', models.DateTimeField(null=True, blank=True)),
                ('stargazers_count', models.IntegerField(default=0)),
                ('watchers_count', models.IntegerField(default=0)),
                ('forks_count', models.IntegerField(default=0)),
                ('open_issues_count', models.IntegerField(default=0)),
                ('github_branch', models.CharField(
                    default='', max_length=256,
                    verbose_name='Github Branch', blank=True)),
                ('commit', models.CharField(max_length=256, blank=True)),
                ('commit_message', models.CharField(
                    max_length=256, blank=True)),
                ('commit_url', models.CharField(
                    max_length=256, blank=True)),
                ('travis_status_url', models.CharField(
                    default='', max_length=256,
                    verbose_name='Travis Build Status', blank=True)),
                ('travis_build_url', models.CharField(
                    default='', max_length=256,
                    verbose_name='Travis Build URL', blank=True)),
                ('owner', models.ForeignKey(
                    related_name='import_tasks',
                    to=settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE
                )),
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
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('message_type', models.CharField(max_length=10)),
                ('message_text', models.CharField(max_length=256)),
                ('task', models.ForeignKey(
                    related_name='messages',
                    to='main.ImportTask',
                    on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Namespace',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('namespace', models.CharField(
                    unique=True, max_length=256,
                    verbose_name='GitHub namespace')),
                ('name', models.CharField(
                    max_length=256, null=True,
                    verbose_name='GitHub name', blank=True)),
                ('avatar_url', models.CharField(
                    max_length=256, null=True,
                    verbose_name='GitHub Avatar URL', blank=True)),
                ('location', models.CharField(
                    max_length=256, null=True,
                    verbose_name='Location', blank=True)),
                ('company', models.CharField(
                    max_length=256, null=True,
                    verbose_name='Location', blank=True)),
                ('email', models.CharField(
                    max_length=256, null=True,
                    verbose_name='Location', blank=True)),
                ('html_url', models.CharField(
                    max_length=256, null=True,
                    verbose_name='URL', blank=True)),
                ('followers', models.IntegerField(
                    null=True, verbose_name='Followers')),
            ],
            options={
                'ordering': ('namespace',),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('source', models.CharField(
                    verbose_name='Source', max_length=20, editable=False)),
                ('github_branch', models.CharField(
                    verbose_name='GitHub Branch', max_length=256,
                    editable=False, blank=True)),
                ('travis_build_url', models.CharField(
                    max_length=256, blank=True)),
                ('travis_status', models.CharField(
                    max_length=256, blank=True)),
                ('commit', models.CharField(
                    max_length=256, blank=True)),
                ('committed_at', models.DateTimeField(null=True)),
                ('commit_message', models.CharField(
                    max_length=256, blank=True)),
                ('messages', django.contrib.postgres.fields.ArrayField(
                    default=list, base_field=models.CharField(
                        max_length=256), editable=False, size=None)),
                ('imports', models.ManyToManyField(
                    verbose_name='Tasks', editable=False,
                    to='main.ImportTask', related_name='notifications')),
                ('owner', models.ForeignKey(
                    related_name='notifications', editable=False,
                    to=settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE)),
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
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('source', models.CharField(
                    max_length=20, verbose_name='Source')),
                ('github_user', models.CharField(
                    max_length=256, verbose_name='Github Username')),
                ('github_repo', models.CharField(
                    max_length=256, verbose_name='Github Repository')),
                ('secret', models.CharField(
                    max_length=256, verbose_name='Secret', db_index=True)),
                ('owner', models.ForeignKey(
                    related_name='notification_secrets',
                    to=settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('source', 'github_user', 'github_repo'),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(max_length=512, db_index=True)),
                ('original_name', models.CharField(max_length=512)),
                ('release', models.CharField(
                    max_length=50,
                    verbose_name='Distribution Release Version')),
                ('alias', models.CharField(
                    max_length=256, null=True,
                    verbose_name='Search terms', blank=True)),
            ],
            options={
                'ordering': ['name', 'release'],
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='RefreshRoleCount',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('state', models.CharField(max_length=20)),
                ('passed', models.IntegerField(default=0, null=True)),
                ('failed', models.IntegerField(default=0, null=True)),
                ('deleted', models.IntegerField(default=0, null=True)),
                ('updated', models.IntegerField(default=0, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('github_user', models.CharField(
                    max_length=256, verbose_name='Github Username')),
                ('github_repo', models.CharField(
                    max_length=256, verbose_name='Github Repository')),
                ('is_enabled', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(
                    related_name='repositories',
                    to=settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('github_user', 'github_repo'),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(
                    auto_now_add=True)),
                ('modified', models.DateTimeField(
                    auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(
                    default=True, db_index=True)),
                ('name', models.CharField(
                    max_length=512, db_index=True)),
                ('original_name', models.CharField(
                    max_length=512)),
                ('role_type', models.CharField(
                    default='ANS', max_length=3, editable=False,
                    choices=[
                        ('ANS', 'Ansible'),
                        ('CON', 'Container Enabled'),
                        ('APP', 'Container App'),
                        ('DEM', 'Demo')])),
                ('namespace', models.CharField(
                    max_length=256, null=True,
                    verbose_name='Namespace', blank=True)),
                ('github_user', models.CharField(
                    max_length=256, verbose_name='Github Username')),
                ('github_repo', models.CharField(
                    max_length=256, verbose_name='Github Repository')),
                ('github_branch', models.CharField(
                    default='', max_length=256,
                    verbose_name='Github Branch', blank=True)),
                ('github_default_branch', models.CharField(
                    default='master', max_length=256,
                    verbose_name='Default Branch')),
                ('readme', models.TextField(
                    default='',
                    verbose_name='README raw content',
                    blank=True)),
                ('readme_type', models.CharField(
                    max_length=5, null=True,
                    verbose_name='README type')),
                ('readme_html', models.TextField(
                    default='', verbose_name='README HTML', blank=True)),
                ('container_yml', models.TextField(
                    null=True, verbose_name='container.yml', blank=True)),
                ('min_ansible_version', models.CharField(
                    max_length=10, null=True,
                    verbose_name='Min Ansible Version', blank=True)),
                ('min_ansible_container_version', models.CharField(
                    max_length=10, null=True, blank=True,
                    verbose_name='Min Ansible Container Version')),
                ('issue_tracker_url', models.CharField(
                    max_length=256, null=True,
                    verbose_name='Issue Tracker URL', blank=True)),
                ('license', models.CharField(
                    max_length=50, verbose_name='License (optional)',
                    blank=True)),
                ('company', models.CharField(
                    max_length=50, null=True,
                    verbose_name='Company Name (optional)',
                    blank=True)),
                ('is_valid', models.BooleanField(
                    default=False, editable=False)),
                ('featured', models.BooleanField(
                    default=False, editable=False)),
                ('travis_status_url', models.CharField(
                    default='', max_length=256,
                    verbose_name='Travis Build Status', blank=True)),
                ('travis_build_url', models.CharField(
                    default='', max_length=256,
                    verbose_name='Travis Build URL', blank=True)),
                ('imported', models.DateTimeField(
                    null=True, verbose_name='Last Import')),
                ('download_count', models.IntegerField(default=0)),
                ('stargazers_count', models.IntegerField(default=0)),
                ('watchers_count', models.IntegerField(default=0)),
                ('forks_count', models.IntegerField(default=0)),
                ('open_issues_count', models.IntegerField(default=0)),
                ('commit', models.CharField(max_length=256, blank=True)),
                ('commit_message', models.CharField(
                    max_length=256, blank=True)),
                ('commit_url', models.CharField(max_length=256, blank=True)),
                ('commit_created', models.DateTimeField(
                    null=True, verbose_name='Laste Commit DateTime')),
                ('bayesian_score', models.FloatField(
                    default=0.0, editable=False)),
                ('num_ratings', models.IntegerField(default=0)),
                ('average_score', models.FloatField(default=0.0)),
                ('categories', models.ManyToManyField(
                    related_name='categories', editable=False,
                    to='main.Category', blank=True, help_text='',
                    verbose_name='Categories')),
                ('cloud_platforms', models.ManyToManyField(
                    related_name='roles', verbose_name='Cloud Platforms',
                    editable=False, to='main.CloudPlatform', blank=True)),
                ('dependencies', models.ManyToManyField(
                    related_name='+', editable=False,
                    to='main.Role', blank=True)),
                ('platforms', models.ManyToManyField(
                    related_name='roles', editable=False,
                    to='main.Platform', blank=True, help_text='',
                    verbose_name='Supported Platforms')),
            ],
            options={
                'ordering': ['namespace', 'name'],
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='RoleRating',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('score', models.IntegerField(default=0, db_index=True)),
                ('owner', models.ForeignKey(
                    related_name='ratings',
                    to=settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE)),
                ('role', models.ForeignKey(
                    related_name='ratings',
                    to='main.Role',
                    on_delete=models.CASCADE)),
            ],
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='RoleVersion',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(max_length=512, db_index=True)),
                ('original_name', models.CharField(max_length=512)),
                ('release_date', models.DateTimeField(null=True, blank=True)),
                ('loose_version', galaxy.main.fields.LooseVersionField(
                    editable=False, db_index=True)),
                ('role', models.ForeignKey(
                    related_name='versions',
                    to='main.Role',
                    on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('-loose_version',),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Stargazer',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('owner', models.ForeignKey(
                    related_name='starred',
                    to=settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE)),
                ('role', models.ForeignKey(
                    related_name='stars',
                    to='main.Role',
                    on_delete=models.CASCADE)),
            ],
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('github_user', models.CharField(
                    max_length=256, verbose_name='Github Username')),
                ('github_repo', models.CharField(
                    max_length=256, verbose_name='Github Repository')),
                ('owner', models.ForeignKey(
                    related_name='subscriptions',
                    to=settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('owner', 'github_user', 'github_repo'),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(
                    unique=True, max_length=512, db_index=True)),
                ('original_name', models.CharField(max_length=512)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Tags',
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='UserAlias',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('alias_name', models.CharField(
                    unique=True, max_length=30)),
                ('alias_of', models.ForeignKey(
                    related_name='aliases',
                    to=settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE
                )),
            ],
            options={
                'verbose_name_plural': 'UserAliases',
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default='', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('url', models.CharField(help_text='', max_length=256)),
                ('role', models.ForeignKey(
                    related_name='videos',
                    to='main.Role',
                    help_text='', null=True,
                    on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'videos',
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AddField(
            model_name='role',
            name='tags',
            field=models.ManyToManyField(
                related_name='roles', editable=False,
                to='main.Tag', blank=True, help_text='',
                verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='notification',
            name='roles',
            field=models.ManyToManyField(
                verbose_name='Roles', editable=False,
                to='main.Role', related_name='notifications'),
        ),
        migrations.AddField(
            model_name='importtask',
            name='role',
            field=models.ForeignKey(
                related_name='import_tasks',
                to='main.Role',
                on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together={('owner', 'github_user', 'github_repo')},
        ),
        migrations.AlterUniqueTogether(
            name='stargazer',
            unique_together={('owner', 'role')},
        ),
        migrations.AlterUniqueTogether(
            name='rolerating',
            unique_together={('owner', 'role')},
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together={('namespace', 'name'),
                             ('github_user', 'github_repo')},
        ),
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together={('owner', 'github_user', 'github_repo')},
        ),
        migrations.AlterUniqueTogether(
            name='notificationsecret',
            unique_together={('source', 'github_user', 'github_repo')},
        ),
        migrations.RunPython(
            code=upgrade_contentblocks_data,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
