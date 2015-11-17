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
import bleach

from celery import task
from github import Github, AuthenticatedUser
from github import GithubException
from urlparse import urlparse

from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import text, html, timezone

from allauth.socialaccount.models import SocialToken

from galaxy.main.models import *

def fail_import_task(import_task, logger, msg):
    transaction.rollback()
    try:
        if import_task:
            import_task.state = "FAILED"
            import_task.messages.create(message_type="ERROR", message_text=msg)        
            import_task.save()
            transaction.commit()
    except Exception, e:
        transaction.rollback()
        print "Error updating import task state for role %s: %s" % (role,str(e))
    print msg
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

def add_message(import_task, msg_type, msg_text):
    try:
        import_task.messages.create(message_type=msg_type,message_text=msg_text)
        import_task.save()
        transaction.commit()
    except Exception, e:
        transaction.rollback()
        print "Error adding message to import task for role %s: %s" % (import_task.role.name,str(e))
    print "Role %d: %s - %s" % (import_task.role.id, msg_type, msg_text)

def get_readme(import_task, repo):
    """
    Retrieve README.md from the repo and sanitize by removing all markup. Should preserve unicode characters.
    """
    add_message(import_task, "INFO", "Parsing and validating README.md")

    # load README.md
    try: 
        if import_task.github_reference:
            readme = repo.get_file_contents("README.md",ref=import_task.github_reference)
        else:
            readme = repo.get_file_contents("README.md")    
    except:
        readme = None
        add_message(import_task, "ERROR", "Failed to find a README.md. All role repositories must include a README.md.")
    
    if not readme is None:
        # decode base64
        try: 
            readme = readme.content.decode('base64')
        except:
            readme = None
            add_messge(import_task, "ERROR", "Failed to base64 decode README.md file.")
    
    if not readme is None:
        # Remove all HTML tags while preserving any unicde chars
        try:
            readme = bleach.clean(readme, strip=True, tags=[])
        except Exception, e:
            add_message(import_task, "ERROR", "Failed to strip HTML tags in README.md: %s" % str(e))
    
    return readme


@task(throws=(Exception,))
def import_role(task_id):
    
    # regex used to strip unwanted substrings from the 
    # role name or from any deps
    name_regex = re.compile(r'^(ansible[-_.+]*)*(role[-_.+]*)*')

    # standard task logger
    logger = import_role.get_logger()

    # get the role from the database
    try:
        print "Starting task: %d" % int(task_id)
        import_task = ImportTask.objects.get(id=task_id)
        import_task.state = "RUNNING"
        import_task.started = datetime.datetime.now()
        import_task.save()
        transaction.commit()
    except:
        fail_import_task(None, logger, "Failed to get task id: %d" % int(task_id))

    try:
        role = Role.objects.get(id=import_task.role.id)
    except:
        fail_import_task(import_task, "Failed to get role for task id: %d" % int(task_id))

    user = import_task.owner
    repo_full_name = role.github_user + "/" + role.github_repo
    add_message(import_task, "INFO", "Starting import %d: role_name=%s repo=%s ref=%s" % 
        (import_task.id,role.name,repo_full_name,import_task.github_reference))

    try:
        token = SocialToken.objects.get(account__user=user, account__provider='github')
    except:
        fail_import_task(import_task, logger,"Failed to get Github account for Galaxy user %s. You must first " +
            "authenticate with Github." % user.username)

    # create an API object and get the repo
    try:
        gh_api = Github(token.token)
        gh_api.get_api_status()
    except:
        fail_import_task(import_task, logger, "Failed to connect to Github API. This is most likely a temporary error, please retry your import in a few minutes.")
    
    try:
        gh_user = gh_api.get_user()
    except:
        fail_import_task(import_task, logger, "Failed to get Github authorized user.")

    repo = None
    add_message(import_task, "INFO", "Retrieving Github repo %s" % repo_full_name)
    for r in gh_user.get_repos():
        if r.full_name == repo_full_name:
            repo = r
            continue
    if repo is None:
        fail_import_task(import_task, logger, "Galaxy user %s does not have access to repo %s" % (user.username,repo_full_name))

    branch = import_task.github_reference if import_task.github_reference else repo.default_branch
    add_message(import_task, "INFO", "Accessing branch: %s" % branch)
        
    # parse and validate meta/main.yml data
    add_message(import_task, "INFO", "Parsing and validating meta/main.yml")
   
    try:
        if import_task.github_reference:
            meta_file = repo.get_file_contents("meta/main.yml", ref=import_task.github_reference)
        else:
            meta_file = repo.get_file_contents("meta/main.yml")    
    except:
        fail_import_task(import_task, logger, "Failed to find meta/main.yml. The role must include a meta/main.yml file.")

    try:
        meta_data = yaml.safe_load(meta_file.content.decode('base64'))
    except Exception, e:
        fail_import_task(import_task, logger, "Failed to parse meta/main.yml. The role must have a valid meta/main.yml file.")
    
    galaxy_info = meta_data.get("galaxy_info", None)
    if galaxy_info is None:
        add_messge(import_task, "ERROR", "Key galaxy_info not found in meta/main.yml")
        galaxy_info = {}

    role.description         = strip_input(galaxy_info.get("description",""))
    role.author              = strip_input(galaxy_info.get("author",""))
    role.company             = strip_input(galaxy_info.get("company",""))
    role.license             = strip_input(galaxy_info.get("license",""))
    role.min_ansible_version = strip_input(galaxy_info.get("min_ansible_version",""))
    role.issue_tracker_url   = strip_input(galaxy_info.get("issue_tracker_url",""))
    role.github_branch       = strip_input(galaxy_info.get("github_branch",repo.default_branch))

    if import_task.github_reference and role.branch != import_task.github_reference:
        fail_import_task(import_task, logger, "Requested branch %s does not match branch %s specified " +
            "in meta/main.yml." % (import_task.github_reference,role.branch))

    if role.issue_tracker_url == "" and repo.has_issues:
        role.issue_tracker_url = repo.issues_url
    
    if role.company != "" and len(role.company) > 50:
        add_message(import_task, "WARNING", "galaxy_info.compnay exceeds max length of 50 in meta/main.yml")
        role.company = role.company[:50]
    
    if role.description == "":
        add_message(import_task, "ERROR", "galaxy_info.description missing value in meta/main.yml")
    elif len(role.description) > 255:
        add_message(import_task, "WARNING", "galaxy_info.description exceeds max length of 255 in meta/main.yml")
        role.description = role.description[:255]
    
    if role.license == "":
        add_message(import_task, "ERROR", "galaxy_info.license missing value in meta/main.yml")
    elif len(role.license) > 50:
        add_message(import_task, "WARNING", "galaxy_info.license exceeds max length of 50 in meta/main.yml")
        role.license = role.license[:50]
        
    if role.min_ansible_version == "":
        add_message(import_task, "WARNING", "galaxy.min_ansible_version missing value in meta/main.yml. Defaulting to 1.2.")
        role.min_ansible_version = '1.2'
    
    if role.issue_tracker_url == "":
        add_message(import_task, "WARNING", "No issue tracker defined. Enable issue tracker in repo settings or define galaxy_info.issue_tracker_url in meta/main.yml.")
    else:
        parsed_url = urlparse(role.issue_tracker_url)
        if parsed_url.scheme == '' or parsed_url.netloc == '' or parsed_url.path == '':
            add_message(impor_task, "WARNING", "Invalid URL provided for galaxy_info.issue_tracker_url in meta/main.yml")
            role.issue_tracker_url = ""

    # Add tags / categories. Remove ':' and only allow alpha-numeric characters
    add_message(import_task, "INFO", "Parsing galaxy_tags")
    meta_tags = []
    if galaxy_info.get("categories", None):
        add_message(import_task, "WARNING", "Found galaxy_info.categories. Update meta/main.yml to use galaxy_info.galaxy_tags.")
        cats = galaxy_info.get("categories")
        if isinstance(cats,basestring) or not hasattr(cats, '__iter__'):
            add_message(import_task, "ERROR","In meta/main.yml galaxy_info.categories must be an iterable list.")
        else:
            for category in cats:
                for cat in category.split(':'): 
                    if re.match('^[a-zA-Z0-9]+$',cat):
                        meta_tags.append(cat)
                    else:
                        add_message(import_task, "WARNING", "%s is not a valid tag" % cat)
    
    if galaxy_info.get("galaxy_tags", None):
        tags = galaxy_info.get("galaxy_tags")
        if isinstance(tags,basestring) or not hasattr(tags, '__iter__'):
            add_message(import_task,"ERROR","In meta/main.yml galaxy_info.galaxy_tags must be an iterable list.")
        else:
            for tag in tags:
                for t in tag.split(':'):
                    if re.match('^[a-zA-Z0-9:]+$',t):
                        meta_tags.append(t)
                    else:
                        add_message(import_task, "WARNING", "%s is not a valid tag" % cat)

    # There are no tags?
    if len(meta_tags) == 0:
        add_message(import_task, "ERROR", "No values found for galaxy_tags. galaxy_info.galaxy_tags must be an iterable list in meta/main.yml")

    if len(meta_tags) > 20:
        add_message(import_task, "WARNING", "Found more than 20 values for galaxy_info.galaxy_tags in meta/main.yml. Only the first 20 will be used.")
        meta_tags = meta_tags[0:20]

    meta_tags = list(set(meta_tags))

    for tag in meta_tags:
        pg_tags = Tag.objects.filter(name=tag).all()
        if len(pg_tags) == 0:
            pg_tag = Tag(name=tag, description=tag, active=True)
            pg_tag.save()
        else:
            pg_tag = pg_tags[0]
        if not role.tags.filter(name=tag).exists():
            role.tags.add(pg_tag)

    # Remove tags no longer listed in the metadata
    for tag in role.tags.all():
        if tag.name not in meta_tags:
            role.tags.remove(tag)

    # Add in the platforms and versions
    add_message(import_task, "INFO", "Parsing platforms")
    meta_platforms = galaxy_info.get("platforms", None)
    if meta_platforms is None:
        add_message(import_task, "ERROR", "galaxy_info.platforms not defined in meta.main.yml. Must be an iterable list.")
    elif isinstance(meta_platforms,basestring) or not hasattr(meta_platforms, '__iter__'):
        add_message(import_task, "ERROR", "Failed to iterate platforms. galaxy_info.platforms must be an iterable list in meta/main.yml.")
    else:
        platform_list = []
        for platform in meta_platforms:
            if not isinstance(platform, dict):
                add_message(import_task, "ERROR", "The platform '%s' does not appear to be a dictionary, skipping" % str(platform))
                continue
            try:
                name     = platform.get("name")
                versions = platform.get("versions", ["all"])
                if not name:
                    add_message(import_task, "ERROR", "No name specified for platform, skipping")
                    continue
                elif not isinstance(versions, list):
                    add_message(import_task, "ERROR", "No name specified for platform %s, skipping" % name)
                    continue

                if len(versions) == 1 and versions == ["all"] or 'all' in versions:
                    # grab all of the objects that start
                    # with the platform name
                    try:
                        platform_objs = Platform.objects.filter(name=name)
                        for p in platform_objs:
                            role.platforms.add(p)
                            platform_list.append("%s-%s" % (name, p.release))
                    except:
                        add_message(import_task, "ERROR", "Invalid platform: %s-all (skipping)" % name)
                else:
                    # just loop through the versions and add them
                    for version in versions:
                        try:
                            p = Platform.objects.get(name=name, release=version)
                            role.platforms.add(p)
                            platform_list.append("%s-%s" % (name, p.release))
                        except:
                            add_message(import_task, "ERROR", "Invalid platform: %s-%s (skipping)" % (name,version))
            except Exception, e:
                add_message(import_task, "ERROR", "An unknown error occurred while adding platform: %s" % str(e))
            
        # Remove platforms/versions that are no longer listed in the metadata
        for platform in role.platforms.all():
            platform_key = "%s-%s" % (platform.name, platform.release)
            if platform_key not in platform_list:
                role.platforms.remove(platform)

    # Add in dependencies (if there are any):
    add_message(import_task, "INFO", "Adding dependencies")
    dependencies = meta_data.get("dependencies", None)

    if dependencies is None:
        add_message(import_task, "ERROR", "meta/main.yml missing definition for dependencies. Define dependencies as [] or an iterable list.")
    elif isinstance(dependencies,basestring) or not hasattr(dependencies, '__iter__'):
        add_message(import_task, "ERROR", "Failed to iterate dependencies. Define dependencies in meta/main.yml as [] or an iterable list.")
    else:
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
                dep_role = Role.objects.get(name=dep_role_name, namespace=dep_user_name)
                role.dependencies.add(dep_role)
                dep_names.append(dep)
            except Exception, e:
                add_message(import_task, "ERROR: Invalid role dependency: %s (skipping) (error: %s)" % (str(dep),e))

        # Remove deps that are no longer listed in the metadata
        for dep in role.dependencies.all():
            dep_name = dep.__unicode__()
            if dep_name not in dep_names:
                role.dependencies.remove(dep)

    role.readme = get_readme(import_task, repo)
    
    # helper function to save repeating code:
    def add_role_version(category):
        rv,created = RoleVersion.objects.get_or_create(name=category.name, role=role)
        rv.release_date = category.commit.commit.author.date
        rv.save()

    # get the tags for the repo, and then loop through them
    # so we can create version objects for the role
    add_message(import_task, "INFO", "Adding repo tags as role versions")
    try:
        git_tag_list = repo.get_tags()
        for git_tag in git_tag_list:
            add_role_version(git_tag)
    except Exception, e:
        add_message(import_task, "ERROR", "An error occurred while importing repo tags: %s" % str(e))
    
    # determine state of import task
    error_count = import_task.messages.filter(message_type="ERROR").count()
    warning_count = import_task.messages.filter(message_type="WARNING").count()
    import_state = "SUCCESS" if error_count == 0 else "FAILED"
    add_message(import_task, "INFO", "Import completed")
    add_message(import_task, import_state, "Status %s : warnings=%d errors=%d" % (import_state,warning_count,error_count))
    
    try:
        import_task.state = import_state
        import_task.save()
        if import_state == "SUCCESS":
            role.is_valid = True
            role.save()
        transaction.commit()
    except Exception, e:
        fail_import_task(import_task, logger, "An error occurred while saving the role: %s" % str(e))
    
    return True


#----------------------------------------------------------------------
# Periodic Tasks
#----------------------------------------------------------------------

@task(name="galaxy.main.celerytasks.tasks.clear_stuck_imports")
def clear_stuck_imports():
    two_hours_ago = timezone.now() - datetime.timedelta(seconds=7200)
    try:
        for ri in ImportTask.objects.filter(created__lte=two_hours_ago, state='PENDING'):
            print "Removing stuck import %s for role %s" % (ri, ri.role)
            ri.state = "FAILED"
            ri.messages.create(
                message_type="ERROR",
                message_text="Import timed out, please try again. If you continue seeing this message you may have a " +
                "syntax error in your meta/main.yml file."
            )
            ri.save()
            transaction.commit()
    except Exception, e:
        print "Exception while clearing stuck imports: %s" % str(e)
    return True
