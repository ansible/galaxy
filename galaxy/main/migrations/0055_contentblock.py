# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import galaxy.main.mixins

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


def downgrade_contentblocks_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_role_type_demo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.SlugField(unique=True)),
                ('content', models.TextField(verbose_name=b'content',
                                             blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.RunPython(upgrade_contentblocks_data,
                             downgrade_contentblocks_data)
    ]
