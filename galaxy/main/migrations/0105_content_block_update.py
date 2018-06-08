# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


MAIN_TITLE_BLOCK = ""

MAIN_SHARE_BLOCK = """
<p>Help other Ansible users by sharing the awesome roles you create.</p>
<p>Maybe you have a role for installing and configuring a popular
   software package, or a role for deploying software built by your
   company. Whatever it is, use Galaxy to share it with the community.</p>
"""

MAIN_DOWNLOADS_BLOCK = """
<p>Jump-start your automation project with great content from the Ansible
   community. Galaxy provides pre-packaged units of work known to Ansible
   as roles.</p>
<p>Roles can be dropped into Ansible PlayBooks and immediately put to work.
   You'll find roles for provisioning infrastructure, deploying applications,
   and all of the tasks you do everyday.</p>
<p>Use the <a href="/search">Search page</a> to find roles for your project,
   then download them onto your Ansible host using
   <a href="https://docs.ansible.com/ansible/latest/reference_appendices/galaxy.html#the-command-line-tool"
   target="_blanck">ansible-galaxy</a>, the command line tool that comes
   bundled with Ansible.</p>
"""

MAIN_FEATURED_BLOG_BLOCK = """
<a href="https://ansible.com/blog" target="_blank">
    Read the latest from The Inside Playbook, and keep up with what's
    happening in the Ansible universe.</a>
"""


def upgrade_contentblocks_data(apps, schema_editor):
    ContentBlock = apps.get_model("main", "ContentBlock")
    db_alias = schema_editor.connection.alias
    ContentBlock.objects.using(db_alias).filter(
        name='main-title').update(content=MAIN_TITLE_BLOCK)
    ContentBlock.objects.using(db_alias).filter(
        name='main-share').update(content=MAIN_SHARE_BLOCK)
    ContentBlock.objects.using(db_alias).filter(
        name='main-downloads').update(content=MAIN_DOWNLOADS_BLOCK)
    ContentBlock.objects.using(db_alias).filter(
        name='main-featured-blog').update(content=MAIN_FEATURED_BLOG_BLOCK)


def downgrade_contentblocks_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0104_repository_version'),
    ]

    operations = [
        migrations.RunPython(upgrade_contentblocks_data,
                             downgrade_contentblocks_data)
    ]
