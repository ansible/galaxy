# (c) 2012-2014, Ansible, Inc. <support@ansible.com>
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import re
import os.path
import time
import yaml
import datetime

from celery import current_task, task
from github import Github

from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import text, html, timezone

from galaxy.main.utils import db_common
from galaxy.main.models import *

def fail_import_task(role, logger, msg):
    transaction.rollback()
    try:
        if role:
            role_import = role.imports.latest()
            if role_import:
                role_import.state = "FAILED"
                role_import.status_message = msg
                role_import.save()
                transaction.commit()
    except Exception, e:
        transaction.rollback()
        logger.error("error while trying to update import task state for role %s: %s" % (role,e))
    logger.error(msg)
    raise Exception(msg)

def strip_input(input):
    """
    A simple helper to strip input strings while checking
    to make sure they're not None.
    """
    if input == None:
        return ""
    elif isinstance(input, basestring):
        return input.strip()
    else:
        return input

@task(throws=(Exception,))
#@transaction.commit_manually
def import_role(role_id, target="all"):
    # regex used to strip unwanted substrings from the 
    # role name or from any deps
    name_regex = re.compile(r'^(ansible[-_.+]*)*(role[-_.+]*)*')

    # standard task logger
    logger = import_role.get_logger()

    # get the role from the database
    try:
        role = Role.objects.get(id=role_id)
        role_import = role.imports.latest()
        role_import.state = "RUNNING"
        role_import.status_message = "Import task is running..."
        role_import.save()
        transaction.commit()
    except:
        fail_import_task(None, logger, "Failed to get the role id: %d. No role was found." % role_id)

    # create an API object and get the repo
    try:
        # FIXME: needs to use a real github account in order in order to
        #        avoid a ridiculously low rate limit (60/hr vs 5000/hr)
        if hasattr(settings, 'GITHUB_API_TOKEN'):
            gh_api = Github(settings.GITHUB_API_TOKEN)
        else:
            gh_api = Github(settings.GITHUB_USERNAME, settings.GITHUB_PASSWORD)
        gh_api.get_api_status()
    except:
        fail_import_task(role, logger, "Failed to connect to the Github API. This is most likely a temporary error, please re-try your import in a few minutes.")
    try:
        user = gh_api.get_user(role.github_user)
        repo = user.get_repo("%s" % role.github_repo)
    except:
        fail_import_task(role, logger, "Failed to get the specified repo: %s/%s. Please make sure it is a public repo on Github." % (role.github_user,role.github_repo))

    # parse and validate meta/main.yml data
    galaxy_info = {}
    dependencies = []
    try:
        meta_file = repo.get_file_contents("meta/main.yml")
        meta_data = yaml.safe_load(meta_file.content.decode('base64'))
        galaxy_info = meta_data.get("galaxy_info", None)
        dependencies = meta_data.get("dependencies", [])
        if not galaxy_info:
            raise Exception("galaxy info not found")
    except Exception, e:
        fail_import_task(role, logger, "Failed to parse 'meta/main.yml'. Please refer to the 'Getting Started' documentation regarding the proper format of the 'meta/main.yml' file. Once the issue has been corrected in the repository, you can retry the import. Real Error: %s" % e)

    # validate README.md
    try:
        readme_file = html.escape(html.strip_tags(repo.get_file_contents("README.md").content.decode('base64')))
    except:
        fail_import_task(role, logger, "Failed to find a README.md. All role repositories must include a README.md. Please refer to the 'Getting Started' documentation regarding role requirements. Once the issue has been corrected in the repsotitory, you can retry the import.")
    # add the new fields 
    try:
        role.readme              = readme_file
        role.description         = strip_input(galaxy_info.get("description",""))
        role.author              = strip_input(galaxy_info.get("author",""))
        role.company             = strip_input(galaxy_info.get("company",""))
        role.license             = strip_input(galaxy_info.get("license",""))
        role.min_ansible_version = strip_input(galaxy_info.get("min_ansible_version","1.2"))
        role.issue_tracker_url   = strip_input(galaxy_info.get("issue_tracker_url",""))
        if role.description == "":
            role.description = repo.description
            if role.description == "":
                raise Exception("The description field cannot be blank.")
        if role.issue_tracker_url == "" and repo.has_issues:
            role.issue_tracker_url = "https://github.com/%s/%s/issues" % (role.github_user, role.github_repo)
    except Exception, e:
        fail_import_task(role, logger, "Failed to update the specified role's fields. Please retry the import in a few minutes. If you continue to receive a failure, please contact support. Error was: %s" % str(e))

    # Add in the categories 
    meta_categories = galaxy_info.get("categories", [])
    if len(meta_categories) == 0:
        fail_import_task(role, logger, "You must specify categories for your role. Make sure the #categories: line is not commented out in your meta/main.yml file.")
    for category in meta_categories:
        try:
            logger.info("getting category: %s" % category)
            category_obj = Category.objects.get(name=category)
            role.categories.add(category_obj)
        except:
            logger.warning("Invalid category: %s (skipping)" % category)

    # Remove categories that are no longer specified in the metadata
    for category in role.categories.all():
        if category.name not in meta_categories:
            logger.info(" category %s is no longer in the metadata, removing it" % category.name)
            role.categories.remove(category)

    # Add in the platforms and versions
    meta_platforms = galaxy_info.get("platforms", [])
    platform_list = []
    for platform in meta_platforms:
        if not isinstance(platform, dict):
            logger.warning("The platform '%s' does not appear to be a dictionary, skipping" % str(platform))
            continue
        try:
            name     = platform.get("name")
            versions = platform.get("versions", ["all"])
            if not name:
                logger.warning("No name specified for this platform, skipping")
                continue
            elif not isinstance(versions, list):
                logger.warning("Versions for this platform is not a list, skipping")
                continue

            if len(versions) == 1 and versions == ["all"] or 'all' in versions:
                # grab all of the objects that start
                # with the platform name
                logger.info("adding all platforms for %s" % name)
                try:
                    platform_objs = Platform.objects.filter(name=name)
                    for p in platform_objs:
                        role.platforms.add(p)
                        platform_list.append("%s-%s" % (name, p.release))
                except:
                    logger.warning("Invalid platform: %s-all (skipping)" % name)
            else:
                # just loop through the versions and add them
                for version in versions:
                    try:
                        logger.info("adding platform: %s-%s" % (name,version))
                        p = Platform.objects.get(name=name, release=version)
                        role.platforms.add(p)
                        platform_list.append("%s-%s" % (name, p.release))
                    except:
                        logger.warning("Invalid platform: %s-%s (skipping)" % (name,version))
        except Exception, e:
            logger.warning("An unknown error occurred while adding platform: %s" % e)

    # Remove platforms/versions that are no longer listed in the metadata
    for platform in role.platforms.all():
        platform_key = "%s-%s" % (platform.name, platform.release)
        if platform_key not in platform_list:
            logger.info(" platform %s is no longer in the meta/main.yml, removing it" % platform_key)
            role.platforms.remove(platform)

    # Add in dependencies (if there are any):
    logger.warning("Adding dependencies")
    dep_names = []
    for dep in dependencies:
        try:
            if isinstance(dep, dict):
                if 'role' not in dep:
                    raise Exception("'role' keyword was not found in the role dictionary")
                else:
                    dep = dep['role']
            elif not isinstance(dep, basestring):
                raise Exception("role dependencies must either be a string or dictionary (was %s)" % type(dep))
            (dep_user_name,dep_role_name) = dep.split(".",1)
            # strip out substrings from the dep role name, to account for 
            # those that may have imported the role previously before this
            # rule existed, that way we don't end up with broken/missing deps
            dep_role_name = name_regex.sub('', dep_role_name)
            dep_role = Role.objects.get(name=dep_role_name, owner__username=dep_user_name)
            role.dependencies.add(dep_role)
            dep_names.append(dep)
        except Exception, e:
            logger.warning("Invalid role dependency: %s (skipping) (error: %s)" % (str(dep),e))

    # Remove deps that are no longer listed in the metadata
    for dep in role.dependencies.all():
        dep_name = dep.__unicode__()
        if dep_name not in dep_names:
            logger.info("dependency %s is no longer listed in the meta/main.yml, removing it" % str(dep))
            role.dependencies.remove(dep)

    # helper function to save repeating code:
    def add_role_version(category):
        rv,created = RoleVersion.objects.get_or_create(name=category.name, role=role)
        if not created:
            # this version already exists
            logger.info("version %s already exists for this role, skipping" % category.name)
            return
        rv.release_date = category.commit.commit.author.date
        rv.save()

    # get the tags for the repo, and then loop through them
    # so we can create version objects for the role
    try:
        git_tag_list = repo.get_tags()
        for git_tag in git_tag_list:
            logger.info("git tag: %s" % git_tag.name)
            if target == "all":
                add_role_version(git_tag)
            elif target == git_tag.tag:
                add_role_version(git_tag)
                break
    except Exception, e:
        fail_import_task(role, logger, "An error occurred while importing versions/categories. Please verify the formatting of your 'meta/main.yml' and ensure that these fields conform to the style specified in the 'Getting Started' documentation. Once the issue has been corrected, you can retry your import")
    # mark the role valid and save it
    try:
        role_import.state = "SUCCESS"
        role_import.status_message = "Import completed successfully"
        role_import.save()

        role.is_valid = True
        role.save()
        transaction.commit()
    except Exception, e:
        fail_import_task(role, logger, "An unknown error occurred while saving the role. Please wait a few minutes and try again. If you continue to receive a failure, please contact support.")
    
    return True

#----------------------------------------------------------------------
# Periodic Tasks
#----------------------------------------------------------------------

@task(name="galaxy.main.celerytasks.tasks.clear_stuck_imports")
#@transaction.commit_manually
def clear_stuck_imports():
    logger = clear_stuck_imports.get_logger()
    two_hours_ago = timezone.now() - datetime.timedelta(seconds=7200)
    try:
        for ri in RoleImport.objects.filter(released__lte=two_hours_ago, state=''):
            logger.info("Removing stuck import %s for role %s" % (ri, ri.role))
            ri.state = "FAILED"
            ri.status_message = "Import timed out, please try again. If you continue seeing this message you may have a syntax error in your meta/main.yml file."
            ri.save()
        transaction.commit()
    except Exception, e:
        logger.error("Exception occurred while clearing stuck imports: %s" % str(e))
    return True
