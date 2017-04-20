# (c) 2012-2016, Ansible by Red Hat
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by
# the Apache Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Apache License for more details.
#
# You should have received a copy of the Apache License
# along with Galaxy.  If not, see <http://www.apache.org/licenses/>.

import re
import yaml
import datetime
import requests
import logging
import pytz

from celery import task
from github import Github
from github import GithubException, UnknownObjectException
from urlparse import urlparse
from requests import HTTPError
from django.utils import timezone
from django.db import transaction
from allauth.socialaccount.models import SocialToken

from ansible.playbook.role.requirement import RoleRequirement
from ansible.errors import AnsibleError

from galaxy.main.models import (Platform,
                                Tag,
                                Role,
                                ImportTask,
                                RoleVersion,
                                Namespace)
from galaxy.main.celerytasks.elastic_tasks import update_custom_indexes
from galaxy.settings import GITHUB_SERVER

logger = logging.getLogger(__name__)


def get_repo_raw(token, repo_name):
    '''
    Access the API directly. Works around PyGitHub's inability to handle repositories that have
    been renamed. When the API redirects to the correct repo, PyGithub returns an incomplete object.

    :param token: Auth token
    :param repo_name: String containing the full repository name, i.e. namespace/repo_name

    :return: dict of repository attributes
    '''
    auth_header = {u'Authorization': u'token ' + token}
    try:
        url = u"{0}/repos/{1}".format(GITHUB_SERVER, repo_name)
        response = requests.get(url, headers=auth_header)
        response.raise_for_status()
        repo = response.json()
        if repo.get('message'):
            raise Exception(repo['message'])
    except HTTPError as exc:
        if re.match('404', exc.message):
            raise UnknownObjectException('404', {u'detail': u"Object not found"})
        raise Exception(exc.message)
    except Exception as exc:
        raise Exception(u"Failed to access GitHub API - {0}".format(exc.message))
    return repo


def get_meta_data(repo):
    '''
    Try to load the meta file from the repo.

    :param repo: Repo object

    :return: Meta file content
    '''
    meta = None

    for meta_file in ["meta/main.yml", "ansible/meta.yml", "meta/main.yaml", "ansible/meta.yaml"]:
        try:
            meta = repo.get_file_contents(meta_file)
        except Exception:
            pass

        if meta:
            break

    return meta


def update_user_repos(github_repos, user):
    '''
    Refresh user repositories. Used by refresh_user_repos task and galaxy.api.views.RefreshUserRepos.
    Returns user.repositories.all() queryset.
    '''
    logger.info("Starting update_user_repos for user {0}".format(user.username))
    repo_dict = dict()
    for repo in github_repos:
        if not repo.private:
            meta_data = get_meta_data(repo)
            if meta_data:
                logger.info("Create or Update repo {0}".format(repo.full_name))
                name = repo.full_name.split('/')
                cnt = Role.objects.filter(github_user=name[0], github_repo=name[1]).count()
                enabled = cnt > 0
                user.repositories.update_or_create(
                    github_user=name[0],
                    github_repo=name[1],
                    defaults={
                        u'github_user': name[0],
                        u'github_repo': name[1],
                        u'is_enabled': enabled
                    })
                repo_dict[repo.full_name] = True

    # Remove any that are no longer present in GitHub
    for repo in user.repositories.all():
        full_name = "{0}/{1}".format(repo.github_user, repo.github_repo)
        if not repo_dict.get(full_name):
            logger.info("Remove from cache {0}".format(full_name))
            repo.delete()

    logger.info("Finished update_user_repos for user {0}".format(user.username))


def refresh_existing_user_repos(token, github_user):
    '''
    Remove repos belonging to the user that are no longer accessible in GitHub,
    or update github_user, github_repo, if it has changed.
    '''
    logger.info("Starting refresh_existing_user_repos for GitHub user {0}".format(github_user.login))
    remove_roles = []
    for role in Role.objects.filter(github_user=github_user.login):
        full_name = "{0}/{1}".format(role.github_user, role.github_repo)
        try:
            repo = get_repo_raw(token, full_name)
            if not repo or not repo.get('name') or not repo.get('owner'):
                continue
            repo_name = repo['name']
            repo_owner = repo['owner']['login']
            if role.github_repo.lower() != repo_name.lower() or role.github_user.lower() != repo_owner.lower():
                logger.info(u'UPDATED: {0} to {1}/{2}'.format(
                    full_name,
                    repo_owner,
                    repo_name
                ))
                role.github_user = repo_owner
                role.github_repo = repo_name
                role.save()
        except UnknownObjectException:
            logger.error(u"NOT FOUND: {0}".format(full_name))
            remove_roles.append(role.id)
        except Exception as exc:
            logger.error(u"Error: refresh_existing_user_repos {0} - {1}".format(full_name, exc.message))

    for role_id in remove_roles:
        try:
            role = Role.objects.get(id=role_id)
            logger.info(u'DELETING: {0}/{1}'.format(role.namespace, role.name))
            role.delete()
        except Exception as exc:
            logger.error(u"Error: refresh_existing_user_repos - {0}".format(exc.message))

    logger.info("Finished refresh_existing_user_repos for GitHub user {0}".format(github_user.login))


def update_namespace(repo):
    # Use GitHub repo to update namespace attributes
    if repo.owner.type == 'Organization':
        namespace, created = Namespace.objects.get_or_create(namespace=repo.organization.login, defaults={
                                                             'name': repo.organization.name,
                                                             'avatar_url': repo.organization.avatar_url,
                                                             'location': repo.organization.location,
                                                             'company': repo.organization.company,
                                                             'email': repo.organization.email,
                                                             'html_url': repo.organization.html_url,
                                                             'followers': repo.organization.followers})
        if not created:
            namespace.avatar_url = repo.organization.avatar_url
            namespace.location = repo.organization.location
            namespace.company = repo.organization.company
            namespace.email = repo.organization.email
            namespace.html_url = repo.organization.html_url
            namespace.followers = repo.organization.followers
            namespace.save()

    else:
        namespace, created = Namespace.objects.get_or_create(namespace=repo.owner.login, defaults={
                                                             'name': repo.owner.name,
                                                             'avatar_url': repo.owner.avatar_url,
                                                             'location': repo.owner.location,
                                                             'company': repo.owner.company,
                                                             'email': repo.owner.email,
                                                             'html_url': repo.owner.html_url,
                                                             'followers': repo.owner.followers})
        if not created:
            namespace.avatar_url = repo.owner.avatar_url
            namespace.location = repo.owner.location
            namespace.company = repo.owner.company
            namespace.email = repo.owner.email
            namespace.html_url = repo.owner.html_url
            namespace.followers = repo.owner.followers
            namespace.save()
    return True


def fail_import_task(import_task, msg):
    """
    Abort the import task and raise an exception
    """
    transaction.rollback()
    try:
        if import_task:
            import_task.state = "FAILED"
            import_task.messages.create(message_type="ERROR", message_text=msg[:255])
            import_task.finished = timezone.now()
            import_task.save()
            transaction.commit()
    except Exception as e:
        transaction.rollback()
        logger.error(u"Error updating import task state %s: %s" % (import_task.role.name, str(e)))
    logger.error(msg)
    raise Exception(msg)


def strip_input(input):
    """
    A simple helper to strip input strings while checking
    to make sure they're not None.
    """
    if input is None:
        return ""
    elif isinstance(input, basestring):
        return input.strip()
    else:
        return input


def add_message(import_task, msg_type, msg_text):
    try:
        import_task.messages.create(message_type=msg_type, message_text=msg_text[:255])
        import_task.save()
        transaction.commit()
    except Exception as e:
        transaction.rollback()
        logger.error(u"Error adding message to import task for role %s: %s" % (import_task.role.name, e.message))
    logger.info(u"Role %d: %s - %s" % (import_task.role.id, msg_type, msg_text))


def get_readme(import_task, repo, branch, token):
    """
    Retrieve README from the repo and sanitize by removing all markup. Should preserve unicode characters.
    """
    add_message(import_task, "INFO", "Parsing and validating README")
    file_type = None
    readme_html = ''
    readme_raw = ''
    headers = {'Authorization': 'token %s' % token, 'Accept': 'application/vnd.github.VERSION.html'}
    url = "https://api.github.com/repos/%s/readme" % repo.full_name
    data = None
    if import_task.github_reference:
        data = {'ref': branch}
    try:
        response = requests.get(url, headers=headers, data=data)
        response.raise_for_status()
        readme_html = response.text
    except Exception as exc:
        add_message(import_task, u"ERROR", u"Failed to get HTML version of README: %s" % unicode(exc))

    readme = ''
    try:
        if import_task.github_reference:
            readme = repo.get_readme(ref=branch)
        else:
            readme = repo.get_readme()
    except:
        pass

    if readme:
        if readme.name == 'README.md':
            file_type = 'md'
        elif readme.name == 'README.rst':
            file_type = 'rst'
        else:
            add_message(import_task, u"ERROR", u"Unable to determine README file type. Expecting file "
                                               u"extension to be one of: .md, .rst")
        readme_raw = readme.decoded_content
    return readme_raw, readme_html, file_type


def parse_yaml(import_task, file_name, file_contents):
    contents = None
    try:
        contents = yaml.safe_load(file_contents)
    except yaml.YAMLError as exc:
        add_message(import_task, u"ERROR", u"YAML parse error: %s" % unicode(exc))
        fail_import_task(import_task, u"Failed to parse %s. Check YAML syntax." % file_name)
    return contents


def decode_file(import_task, repo, branch, file_name, return_yaml=False):
    try:
        contents = repo.get_file_contents(file_name, ref=branch)
    except Exception:
        return None

    try:
        contents = contents.content.decode('base64')
    except Exception as exc:
        fail_import_task(import_task, u"Failed to decode %s - %s" % (file_name, unicode(exc)))

    if not return_yaml:
        return contents
    return parse_yaml(import_task, file_name, contents)


def add_platforms(import_task, galaxy_info, role):
    add_message(import_task, u"INFO", u"Parsing platforms")
    meta_platforms = galaxy_info.get("platforms", None)
    if isinstance(meta_platforms, basestring) or not hasattr(meta_platforms, '__iter__'):
        add_message(import_task, u"ERROR", u"Expected platforms in meta data to be a list.")
        return
    platform_list = []
    for platform in meta_platforms:
        if not isinstance(platform, dict):
            add_message(import_task, u"ERROR", u"The platform '%s' does not appear to be a dictionary, "
                                               u"skipping" % str(platform))
            continue
        try:
            if not platform.get("name"):
                add_message(import_task, u"ERROR", u"No name specified for platform, skipping")
                continue
            name = platform.get("name")
            versions = platform.get("versions", ["all"])
            if 'all' in versions:
                # grab all of the objects that start with the platform name
                try:
                    platform_objs = Platform.objects.filter(name=name)
                    for p in platform_objs:
                        role.platforms.add(p)
                        platform_list.append("%s-%s" % (name, p.release))
                except:
                    add_message(import_task, u"ERROR", u"Invalid platform: %s-all (skipping)" % name)
                continue
            for version in versions:
                try:
                    p = Platform.objects.get(name=name, release=version)
                    role.platforms.add(p)
                    platform_list.append(u"%s-%s" % (name, p.release))
                except:
                    add_message(import_task, u"ERROR", u"Invalid platform: %s-%s (skipping)" %
                                (name,version))
        except Exception as exc:
            add_message(import_task, u"ERROR", u"An unknown error occurred while adding platform: %s" % unicode(exc))

    # Remove platforms/versions that are no longer listed in the metadata
    for platform in role.platforms.all():
        platform_key = "%s-%s" % (platform.name, platform.release)
        if platform_key not in platform_list:
            role.platforms.remove(platform)


def add_dependencies(import_task, dependencies, role):
    if not dependencies:
        return
    add_message(import_task, u"INFO", u"Adding dependencies")
    if not isinstance(dependencies, list):
        add_message(import_task, "ERROR", "Expected dependencies to be a list, "
                                          "instead got %s" % type(dependencies).__name__)
        return
    dep_names = []
    for dep in dependencies:
        try:
            dep_parsed = RoleRequirement.role_yaml_parse(dep)
            if not dep_parsed.get('name'):
                raise Exception(u"Unable to determine name for dependency")
            names = dep_parsed['name'].split(".")
            if len(names) < 2:
                raise Exception(u"Expecting dependency name format to match 'username.role_name', "
                                u"instead got %s" % dep_parsed['name'])
            if len(names) > 2:
                # the username contains .
                name = names.pop()
                namespace = '.'.join(names)
            else:
                namespace = names[0]
                name = names[1]
            try:
                dep_role = Role.objects.get(namespace=namespace, name=name)
                role.dependencies.add(dep_role)
                dep_names.append(dep_parsed['name'])
            except Exception as exc:
                logger.error("Error loading dependencies %s" % unicode(exc))
                raise Exception(u"Role dependency not found: %s.%s" % (namespace, name))
        except (AnsibleError, Exception) as exc:
            add_message(import_task, u'ERROR', u'Error parsing dependency %s' % unicode(exc))

    # Remove deps that are no longer listed in the metadata
    for dep in role.dependencies.all():
        dep_name = dep.__unicode__()
        if dep_name not in dep_names:
            role.dependencies.remove(dep)


def add_tags(import_task, galaxy_info, role):
    # Add tags / categories. Remove ':' and only allow alpha-numeric characters
    add_message(import_task, u"INFO", u"Parsing galaxy_tags")
    meta_tags = []
    if galaxy_info.get("categories"):
        add_message(import_task, u"WARNING", (u"Found categories in meta data. Update the meta data to use "
                                              u"galaxy_tags rather than categories."))
        cats = galaxy_info.get("categories")
        if not isinstance(cats, list):
            add_message(import_task, u"ERROR", u"Expected categories in meta data to be a list")
        else:
            for category in cats:
                for cat in category.split(':'):
                    if re.match('^[a-zA-Z0-9]+$',cat):
                        meta_tags.append(cat)
                    else:
                        add_message(import_task, u"WARNING", u"%s is not a valid tag" % cat)

    if galaxy_info.get("galaxy_tags"):
        tags = galaxy_info.get("galaxy_tags")
        if not isinstance(tags, list):
            add_message(import_task, u"ERROR", u"Expected galaxy_tags in meta data to be a list.")
        else:
            for tag in tags:
                for t in tag.split(':'):
                    if re.match('^[a-zA-Z0-9:]+$',t):
                        meta_tags.append(t)
                    else:
                        add_message(import_task, u"WARNING", u"'%s' is not a valid tag. Skipping." % t)

    if len(meta_tags) == 0:
        add_message(import_task, u"WARNING", u"No galaxy_tags found in meta data.")

    if len(meta_tags) > 20:
        add_message(import_task, u"WARNING", u"Found more than 20 galaxy_tag values in the meta data. "
                                             u"Only the first 20 will be used.")
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


@task(throws=(Exception,), name="galaxy.main.celerytasks.tasks.import_role")
def import_role(task_id):
    try:
        logger.info(u"Starting task: %d" % int(task_id))
        import_task = ImportTask.objects.get(id=task_id)
        import_task.state = "RUNNING"
        import_task.started = timezone.now()
        import_task.save()
        transaction.commit()
    except:
        fail_import_task(None, u"Failed to get task id: %d" % int(task_id))

    try:
        role = Role.objects.get(id=import_task.role.id)
    except:
        fail_import_task(import_task, u"Failed to get role for task id: %d" % int(task_id))

    repo_full_name = role.github_user + "/" + role.github_repo
    add_message(import_task, u"INFO", u"Starting import %d: role_name=%s repo=%s" % (import_task.id,
                                                                                     role.name,
                                                                                     repo_full_name))
    user = import_task.owner
    try:
        token = SocialToken.objects.get(account__user=user, account__provider='github')
    except:
        fail_import_task(import_task, (u"Failed to get GitHub account for Galaxy user %s. You must first "
                                       u"authenticate with GitHub." % user.username))
    # create an API object and get the repo
    try:
        gh_api = Github(token.token)
        gh_api.get_api_status()
    except:
        fail_import_task(import_task, (u'Failed to connect to the GitHub API. This is most likely a temporary error, '
                                       u'please retry your import in a few minutes.'))

    try:
        repo = gh_api.get_repo(repo_full_name)
    except Exception as exc:
        fail_import_task(import_task, u"Failed to get repo: %s - %s" % (repo_full_name, exc.message))

    if not repo:
        fail_import_task(import_task, u"Failed to find repo: %s" % repo_full_name)

    update_namespace(repo)

    # determine which branch to use
    if import_task.github_reference:
        branch = import_task.github_reference
    elif role.github_branch:
        branch = role.github_branch
    else:
        branch = repo.default_branch
    
    add_message(import_task, u"INFO", u"Accessing branch: %s" % branch)
        
    # parse meta data
    add_message(import_task, u"INFO", u"Parsing and validating meta data.")

    for meta_file in ["meta/main.yml", "ansible/meta.yml", "meta/main.yaml", "ansible/meta.yaml"]:
        meta_data = decode_file(import_task, repo, branch, meta_file, return_yaml=True)

        if meta_data:
            break

    if not meta_data:
        fail_import_task(import_task, u"Failed to get meta data. Did you forget to add meta/main.yml or "
                                      u"ansible/meta.yml?")

    # validate meta/main.yml
    galaxy_info = meta_data.get("galaxy_info", None)
    if galaxy_info is None:
        add_message(import_task, u"ERROR", u"Key galaxy_info not found in meta data")
        galaxy_info = {}

    if import_task.alternate_role_name:
        add_message(import_task, u"INFO", u"Setting role name to %s" % import_task.alternate_role_name)
        role.name = import_task.alternate_role_name

    role.description         = strip_input(galaxy_info.get("description",repo.description))
    role.author              = strip_input(galaxy_info.get("author", ""))
    role.company             = strip_input(galaxy_info.get("company", ""))
    role.license             = strip_input(galaxy_info.get("license", ""))
    if galaxy_info.get('min_ansible_version'):
        role.min_ansible_version = strip_input(galaxy_info.get("min_ansible_version", ""))
    if galaxy_info.get('min_ansible_container_version'):
        role.min_ansible_container_version = strip_input(galaxy_info.get("min_ansible_container_version", ""))
    role.issue_tracker_url   = strip_input(galaxy_info.get("issue_tracker_url", ""))
    role.github_branch       = strip_input(galaxy_info.get("github_branch", ""))
    role.github_default_branch = repo.default_branch

    # check if meta/container.yml exists
    container_yml = decode_file(import_task, repo, branch, 'meta/container.yml', return_yaml=False)
    ansible_container_yml = decode_file(import_task, repo, branch, 'ansible/container.yml', return_yaml=False)
    if container_yml and ansible_container_yml:
        add_message(import_task, u"ERROR", (u"Found ansible/container.yml and meta/container.yml. "
                                            u"A role can only have only one container.yml file."))
    elif container_yml:
        add_message(import_task, u"INFO", u"Found meta/container.yml")
        add_message(import_task, u"INFO", u"Setting role type to Container")
        role.role_type = Role.CONTAINER
        role.container_yml = container_yml
    elif ansible_container_yml:
        add_message(import_task, u"INFO", u"Found ansible/container.yml")
        add_message(import_task, u"INFO", u"Setting role type to Container App")
        role.role_type = Role.CONTAINER_APP
        role.container_yml = ansible_container_yml
    else:
        role.role_type = role.ANSIBLE
        role.container_yml = None

    if role.issue_tracker_url == "" and repo.has_issues:
        role.issue_tracker_url = repo.html_url + '/issues'
    
    if role.company != "" and len(role.company) > 50:
        add_message(import_task, u"WARNING", u"galaxy_info.company exceeds max length of 50 in meta data")
        role.company = role.company[:50]

    if not role.description:
        add_message(import_task, u"ERROR", u"missing description. Add a description to GitHub repo or meta data.")
    elif len(role.description) > 255:
        add_message(import_task, u"WARNING", u"galaxy_info.description exceeds max length of 255 in meta data")
        role.description = role.description[:255]

    if not role.license:
        add_message(import_task, u"ERROR", u"galaxy_info.license missing value in meta data")
    elif len(role.license) > 50:
        add_message(import_task, u"WARNING", u"galaxy_info.license exceeds max length of 50 in meta data")
        role.license = role.license[:50]

    if role.role_type in (role.CONTAINER, role.ANSIBLE) and not role.min_ansible_version:
        add_message(import_task, u"WARNING", u"Minimum Ansible version missing in meta data. Defaulting to 1.9.")
        role.min_ansible_version = u'1.9'

    if role.role_type == role.CONTAINER_APP and not role.min_ansible_container_version:
        add_message(import_task, u"WARNING", u"Minimum Ansible Container version missing in meta data. "
                                             u"Defaulting to 0.2.0")
        role.min_ansible_container_version = u'0.2.0'

    if not role.issue_tracker_url:
        add_message(import_task, u"WARNING", (u"No issue tracker defined. Enable issue tracker in repo settings, "
                                              u"or provide an issue tracker in meta data."))
    else:
        parsed_url = urlparse(role.issue_tracker_url)
        if parsed_url.scheme == '' or parsed_url.netloc == '' or parsed_url.path == '':
            add_message(import_task, u"WARNING", u"Invalid URL found in meta data for issue tracker ")
            role.issue_tracker_url = ""

    # Update role attributes from repo
    sub_count = 0
    for sub in repo.get_subscribers():
        sub_count += 1   # only way to get subscriber count via pygithub
    role.stargazers_count = repo.stargazers_count
    role.watchers_count = sub_count
    role.forks_count = repo.forks_count
    role.open_issues_count = repo.open_issues_count 

    last_commit = repo.get_commits(sha=branch)[0].commit
    role.commit = last_commit.sha
    role.commit_message = last_commit.message[:255]
    role.commit_url = last_commit.html_url
    role.commit_created = last_commit.committer.date.replace(tzinfo=pytz.UTC)

    # Update the import task in the event the role is left in an invalid state.
    import_task.stargazers_count = repo.stargazers_count
    import_task.watchers_count = sub_count
    import_task.forks_count = repo.forks_count
    import_task.open_issues_count = repo.open_issues_count 

    import_task.commit = last_commit.sha
    import_task.commit_message = last_commit.message[:255]
    import_task.commit_url = last_commit.html_url
    import_task.github_branch = branch
    
    add_tags(import_task, galaxy_info, role)
    if role.role_type in (role.CONTAINER, role.ANSIBLE):
        if not galaxy_info.get('platforms'):
            add_message(import_task, u"ERROR", u"No platforms found in meta data")
        else:
            add_platforms(import_task, galaxy_info, role)

    if role.role_type in (role.CONTAINER, role.ANSIBLE) and meta_data.get('dependencies'):
        add_dependencies(import_task, meta_data['dependencies'], role)

    readme, readme_html, readme_type = get_readme(import_task, repo, branch, token)
    if readme:
        role.readme = readme
        role.readme_html = readme_html
        role.readme_type = readme_type
    else:
        fail_import_task(import_task, u"Failed to get README. All roles must include a README.")

    # iterate over repo tags and create version objects
    add_message(import_task, u"INFO", u"Adding repo tags as role versions")
    git_tag_list = []
    try:
        git_tag_list = repo.get_tags()
        for tag in git_tag_list:
            rv, created = RoleVersion.objects.get_or_create(name=tag.name, role=role)
            rv.release_date = tag.commit.commit.author.date.replace(tzinfo=pytz.UTC)
            rv.save()
    except Exception as exc:
        add_message(import_task, u"ERROR", u"An error occurred while importing repo tags: %s" % unicode(exc))

    add_message(import_task, u"INFO", u"Removing old tags")
    if git_tag_list:
        remove_versions = []
        try:
            for version in role.versions.all():
                found = False
                for tag in git_tag_list:
                    if tag.name == version.name:
                        found = True
                        break
                if not found:
                    remove_versions.append(version.name)
        except Exception as exc:
            fail_import_task(import_task, u"Error identifying tags to remove: %s" % unicode(exc))

        if remove_versions:
            try:
                for version_name in remove_versions:
                    RoleVersion.objects.filter(name=version_name, role=role).delete()
            except Exception as exc:
                fail_import_task(import_task, u"Error removing tags from role: %s" % unicode(exc))
    try:
        role.validate_char_lengths()
    except Exception as exc:
        add_message(import_task, u"ERROR", unicode(exc))

    try:
        import_task.validate_char_lengths()
    except Exception as exc:
        add_message(import_task, u"ERROR", unicode(exc))

    # determine state of import task
    error_count = import_task.messages.filter(message_type="ERROR").count()
    warning_count = import_task.messages.filter(message_type="WARNING").count()
    import_state = u"SUCCESS" if error_count == 0 else u"FAILED"
    add_message(import_task, u"INFO", u"Import completed")
    add_message(import_task, import_state, u"Status %s : warnings=%d errors=%d" % (import_state,
                                                                                   warning_count,
                                                                                   error_count))

    try:
        import_task.state = import_state
        import_task.finished = timezone.now()
        import_task.save()
        role.imported = timezone.now()
        role.is_valid = True
        role.save()
        transaction.commit()
    except Exception, e:
        fail_import_task(import_task, u"Error saving role: %s" % e.message)

    # Update ES indexes
    update_custom_indexes.delay(username=role.namespace,
                                tags=role.get_tags(),
                                platforms=role.get_unique_platforms())
    return True


@task(name="galaxy.main.celerytasks.tasks.refresh_user_repos", throws=(Exception,))
@transaction.atomic
def refresh_user_repos(user, token):
    logger.info(u"Refreshing User Repo Cache for {}".format(user.username))

    try:
        gh_api = Github(token)
    except GithubException as exc:
        user.cache_refreshed = True
        user.save()
        msg = u"User {0} Repo Cache Refresh Error: {1}".format(user.username, unicode(exc))
        logger.error(msg)
        raise Exception(msg)

    try:
        ghu = gh_api.get_user()
    except GithubException as exc:
        user.cache_refreshed = True
        user.save()
        msg = u"User {0} Repo Cache Refresh Error: {1}".format(user.username, unicode(exc))
        logger.error(msg)
        raise Exception(msg)

    try:
        repos = ghu.get_repos()
    except GithubException as exc:
        user.cache_refreshed = True
        user.save()
        msg = u"User {0} Repo Cache Refresh Error: {1}".foramt(user.username, unicode(exc))
        logger.error(msg)
        raise Exception(msg)

    refresh_existing_user_repos(token, ghu)

    update_user_repos(repos, user)
    user.github_avatar = ghu.avatar_url
    user.github_user = ghu.login
    user.cache_refreshed = True
    user.save()


@task(name="galaxy.main.celerytasks.tasks.refresh_user_stars", throws=(Exception,))
@transaction.atomic
def refresh_user_stars(user, token):
    logger.info(u"Refreshing User Stars for {}".format(user.username))

    try:
        gh_api = Github(token)
    except GithubException as exc:
        msg = u"User {0} Refresh Stars: {1}".format(user.username, unicode(exc))
        logger.error(msg)
        raise Exception(msg)

    try:
        ghu = gh_api.get_user()
    except GithubException as exc:
        msg = u"User {0} Refresh Stars: {1}" % (user.username, unicode(exc))
        logger.error(msg)
        raise Exception(msg)

    try:
        subscriptions = ghu.get_subscriptions()
    except GithubException as exc:
        msg = u"User {0} Refresh Stars: {1]" % (user.username, unicode(exc))
        logger.error(msg)
        raise Exception(msg)

    # Refresh user subscriptions class
    user.subscriptions.all().delete()
    for s in subscriptions:
        name = s.full_name.split('/')
        cnt = Role.objects.filter(github_user=name[0], github_repo=name[1]).count()
        if cnt > 0:
            user.subscriptions.get_or_create(
                github_user=name[0],
                github_repo=name[1],
                defaults={
                    'github_user': name[0],
                    'github_repo': name[1]
                })
    
    try:
        starred = ghu.get_starred()
    except GithubException as exc:
        msg = u"User {0} Refresh Stars: {1}".format(user.username, unicode(exc))
        logger.error(msg)
        raise Exception(msg)

    # Refresh user starred cache
    user.starred.all().delete()
    for s in starred:
        name = s.full_name.split('/')
        cnt = Role.objects.filter(github_user=name[0], github_repo=name[1]).count()
        if cnt > 0:
            user.starred.get_or_create(
                github_user=name[0],
                github_repo=name[1],
                defaults={
                    'github_user': name[0],
                    'github_repo': name[1]    
                })


@task(name="galaxy.main.celerytasks.tasks.refresh_role_counts")
def refresh_role_counts(start, end, token, tracker):
    '''
    Update each role with latest counts from GitHub
    '''
    tracker.state = 'RUNNING'
    tracker.save()
    passed = 0
    failed = 0
    deleted = 0
    updated = 0
    for role in Role.objects.filter(is_valid=True, active=True, id__gt=start, id__lte=end):
        full_name = "%s/%s" % (role.github_user, role.github_repo)
        try:
            repo = get_repo_raw(token, full_name)
            if not repo:
                raise Exception("Object is empty or NoneType")
            if not repo.get('name') or not repo.get('owner'):
                raise Exception("Object missing name and/or owner attributes")
            repo_name = repo['name']
            repo_owner = repo['owner']['login']
            if role.github_repo.lower() != repo_name.lower() or role.github_user.lower() != repo_owner.lower():
                updated += 1
                logger.info(u'UPDATED: {0} to {1}/{2}'.format(
                    full_name,
                    repo_owner,
                    repo_name
                ))
                role.github_user = repo_owner
                role.github_repo = repo_name
                role.save()
            else:
                passed += 1
        except UnknownObjectException:
            logger.error(u"NOT FOUND: {0}".format(full_name))
            role.delete()
            deleted += 1
        except Exception as exc:
            logger.error(u"FAILED: {0} - {1}".format(full_name, unicode(exc)))
            failed += 1

    tracker.state = 'FINISHED'
    tracker.passed = passed
    tracker.failed = failed
    tracker.deleted = deleted
    tracker.updated = updated
    tracker.save()


# ----------------------------------------------------------------------
# Periodic Tasks
# ----------------------------------------------------------------------

@task(name="galaxy.main.celerytasks.tasks.clear_stuck_imports")
def clear_stuck_imports():
    one_hours_ago = timezone.now() - datetime.timedelta(seconds=3600)
    logger.info(u"Clear Stuck Imports: {}".format(one_hours_ago.strftime("%Y-%m-%d %H:%M:%S")).encode('utf-8').strip())
    try:
        for ri in ImportTask.objects.filter(created__lte=one_hours_ago, state__in=['PENDING', 'RUNNING']):
            logger.info(u"Clear Stuck Imports: {0} - {1}.{2}"
                        .format(ri.id, ri.role.namespace, ri.role.name))
            ri.state = u"FAILED"
            ri.messages.create(
                message_type=u"ERROR",
                message_text=(u"Import timed out, please try again. If you continue seeing this message you may "
                              u"have a syntax error in your meta/main.yml file.")
            )
            ri.save()
            transaction.commit()
    except Exception as exc:
        logger.error(u"Clear Stuck Imports ERROR: {}".format(unicode(exc)))
        raise
