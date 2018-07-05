# (c) 2012-2018, Ansible by Red Hat
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

import codecs
import os
import yaml

from ansiblereview import Result, Error, Standard, lintcheck
from ansiblereview.utils.yamlindent import yamlreview
from ansiblereview.inventory import parse, no_vars_in_host_file
from ansiblereview.vars import repeated_vars
from ansiblereview.playbook import repeated_names
from ansiblereview.rolesfile import yamlrolesfile
from ansiblereview.tasks import yaml_form_rather_than_key_value
from ansiblereview.groupvars import same_variable_defined_in_competing_groups
from ansiblelint.utils import parse_yaml_linenumbers


def rolesfile_contains_scm_in_src(candidate, settings):
    result = Result(candidate.path)
    if candidate.path.endswith(".yml") and os.path.exists(candidate.path):
        try:
            with codecs.open(candidate.path, mode='rb', encoding='utf-8') as f:
                roles = parse_yaml_linenumbers(f.read(), candidate.path)
            for role in roles:
                if '+' in role.get('src'):
                    error = Error(role['__line__'], "Use scm key rather "
                                  "than src: scm+url")
                    result.errors.append(error)
        except Exception as e:
            result.errors = [Error(None, "Cannot parse YAML from %s: %s" %
                                   (candidate.path, str(e)))]
    return result


def files_should_have_actual_content(candidate, settings):
    errors = []
    with codecs.open(candidate.path, mode='rb', encoding='utf-8') as f:
        content = yaml.safe_load(f.read())
    if not content:
        errors = [Error(None, "%s appears to have no useful content" % candidate)]
    return Result(candidate.path, errors)


def host_vars_exist(candidate, settings):
    return Result(candidate.path, [Error(None, "Host vars are generally "
                                         "not required")])


def noop(candidate, settings):
    return Result(candidate.path)


rolesfile_should_be_in_yaml = Standard(dict(
    name="Roles file should be in yaml format",
    check=yamlrolesfile,
    types=["rolesfile"]
))

role_must_contain_meta_main = Standard(dict(
    name="Roles must contain suitable meta/main.yml",
    check=lintcheck('EXTRA0012'),
    types=["meta"]
))

role_meta_main_must_contain_info = Standard(dict(
    name="Roles meta/main.yml must contain important info",
    check=lintcheck('EXTRA0013'),
    types=["meta"]
))

variables_should_contain_whitespace = Standard(dict(
    name="Variable uses should contain whitespace",
    check=lintcheck('EXTRA0001'),
    types=["playbook", "task", "handler", "rolevars",
           "hostvars", "groupvars", "template"]
))

commands_should_be_idempotent = Standard(dict(
    name="Commands should be idempotent",
    check=lintcheck('ANSIBLE0012'),
    types=["playbook", "task"]
))

commands_should_not_be_used_in_place_of_modules = Standard(dict(
    name="Commands should not be used in place of modules",
    check=lintcheck('ANSIBLE0006,ANSIBLE0007'),
    types=["playbook", "task", "handler"]
))

package_installs_should_not_use_latest = Standard(dict(
    name="Package installs should use present, not latest",
    check=lintcheck('ANSIBLE0010'),
    types=["playbook", "task", "handler"]
))

use_shell_only_when_necessary = Standard(dict(
    name="Shell should only be used when essential",
    check=lintcheck('ANSIBLE0013'),
    types=["playbook", "task", "handler"]
))

files_should_be_indented = Standard(dict(
    name="YAML should be correctly indented",
    check=yamlreview,
    types=["playbook", "task", "handler", "rolevars",
           "hostvars", "groupvars", "meta"]
))

inventory_must_parse = Standard(dict(
    name="Inventory must be parseable",
    check=parse,
    types=["inventory"]
))

inventory_hostfiles_should_not_contain_vars = Standard(dict(
    name="Inventory host files should not "
         "contain variable stanzas ([group:vars])",
    check=no_vars_in_host_file,
    types=["inventory"]
))

tasks_are_named = Standard(dict(
    name="Tasks and handlers must be named",
    check=lintcheck('ANSIBLE0011'),
    types=["playbook", "task", "handler"],
))

tasks_are_uniquely_named = Standard(dict(
    name="Tasks and handlers must be uniquely named within a single file",
    check=repeated_names,
    types=["playbook", "task", "handler"],
))

vars_are_not_repeated_in_same_file = Standard(dict(
    name="Vars should only occur once per file",
    check=repeated_vars,
    types=["rolevars", "hostvars", "groupvars"],
))

no_command_line_environment_variables = Standard(dict(
    name="Environment variables should be passed through the environment key",
    check=lintcheck('ANSIBLE0014'),
    types=["playbook", "task", "handler"]
))

no_lineinfile = Standard(dict(
    name="Lineinfile module should not be used as it suggests "
         "more than one thing is managing a file",
    check=lintcheck('EXTRA0002'),
    types=["playbook", "task", "handler"]
))

become_rather_than_sudo = Standard(dict(
    name="Use become/become_user/become_method rather than sudo/sudo_user",
    check=lintcheck('ANSIBLE0008'),
    types=["playbook", "task", "handler"]
))

use_yaml_rather_than_key_value = Standard(dict(
    name="Use YAML format for tasks and handlers rather than key=value",
    check=yaml_form_rather_than_key_value,
    types=["playbook", "task", "handler"]
))

roles_scm_not_in_src = Standard(dict(
    name="Use scm key rather than src: scm+url",
    check=rolesfile_contains_scm_in_src,
    types=["rolesfile"]
))

files_should_not_be_purposeless = Standard(dict(
    name="Files should contain useful content",
    check=files_should_have_actual_content,
    types=["playbook", "task", "handler", "rolevars", "defaults", "meta"]
))

playbooks_should_not_contain_logic = Standard(dict(
    name="Playbooks should not contain logic (vars, tasks, handlers)",
    check=lintcheck('EXTRA0008'),
    types=["playbook"]
))

host_vars_should_not_be_present = Standard(dict(
    name="Host vars should not be present",
    check=host_vars_exist,
    types=["hostvars"]
))

with_items_bare_words = Standard(dict(
    name="bare words are deprecated for with_items",
    check=lintcheck('ANSIBLE0015'),
    types=["task", "handler", "playbook"],
    version="0.0"
))

file_permissions_are_octal = Standard(dict(
    name="octal file permissions should start with a leading zero",
    check=lintcheck('ANSIBLE0009'),
    types=["task", "handler", "playbook"]
))

inventory_hostsfile_has_group_vars = Standard(dict(
    name="inventory file should not contain group variables",
    check=lintcheck('EXTRA0009'),
    types=["inventory"]
))

inventory_hostsfile_has_host_vars = Standard(dict(
    name="inventory file should not contain host variables "
         "(except e.g. ansible_host, ansible_user, etc.)",
    check=lintcheck('EXTRA0010'),
    types=["inventory"]
))

test_matching_groupvar = Standard(dict(
    check=same_variable_defined_in_competing_groups,
    name="Same variable defined in siblings",
    types=["groupvars"]
))

hosts_should_not_be_localhost = Standard(dict(
    check=lintcheck('EXTRA0007'),
    name="Use connection: local rather than hosts: localhost",
    types=["playbook"]
))

# tasks_should_not_use_action =

use_handlers_rather_than_when_changed = Standard(dict(
    check=lintcheck('ANSIBLE0016'),
    name="Use handlers rather than when: changed in tasks",
    types=['task', 'playbook']
))

most_files_shouldnt_have_tabs = Standard(dict(
    check=lintcheck('EXTRA0005'),
    name="Don't use tabs in almost anything that isn't a Makefile",
    types=["playbook", "task", "handler", "rolevars", "defaults", "meta",
           "code", "groupvars", "hostvars", "inventory", "doc", "template",
           "file"]
))

dont_delegate_to_localhost = Standard(dict(
    check=lintcheck('EXTRA0004'),
    name="Use connection: local rather than delegate_to: localhost",
    types=["playbook", "task", "handler"]
))

become_user_should_have_become = Standard(dict(
    check=lintcheck('ANSIBLE0017'),
    name="become_user should be accompanied by become",
    types=["playbook", "task", "handler"]
))

dont_compare_to_literal_bool = Standard(dict(
    check=lintcheck('EXTRA0014'),
    name="Don't compare to True or False - use `when: var` or `when: not var`",
    types=["playbook", "task", "handler", "template"]
))

dont_compare_to_empty_string = Standard(dict(
    check=lintcheck('EXTRA0015'),
    name="Don't compare to \"\" - use `when: var` or `when: not var`",
    types=["playbook", "task", "handler", "template"]
))

# Update this every time standards version increase
latest_version = Standard(dict(
    check=noop,
    name="No-op check to ensure latest standards version is set",
    version="0.1",
    types=[]
))

ansible_min_version = '2.1'
ansible_review_min_version = '0.12.0'
ansible_lint_min_version = '3.4.0'

standards = [
    rolesfile_should_be_in_yaml,
    role_must_contain_meta_main,
    role_meta_main_must_contain_info,
    become_rather_than_sudo,
    variables_should_contain_whitespace,
    commands_should_be_idempotent,
    commands_should_not_be_used_in_place_of_modules,
    package_installs_should_not_use_latest,
    files_should_be_indented,
    use_shell_only_when_necessary,
    inventory_must_parse,
    inventory_hostfiles_should_not_contain_vars,
    tasks_are_named,
    tasks_are_uniquely_named,
    vars_are_not_repeated_in_same_file,
    no_command_line_environment_variables,
    no_lineinfile,
    use_yaml_rather_than_key_value,
    roles_scm_not_in_src,
    files_should_not_be_purposeless,
    playbooks_should_not_contain_logic,
    host_vars_should_not_be_present,
    with_items_bare_words,
    file_permissions_are_octal,
    inventory_hostsfile_has_host_vars,
    inventory_hostsfile_has_group_vars,
    test_matching_groupvar,
    hosts_should_not_be_localhost,
    dont_delegate_to_localhost,
    most_files_shouldnt_have_tabs,
    use_handlers_rather_than_when_changed,
    become_user_should_have_become,
    dont_compare_to_empty_string,
    dont_compare_to_literal_bool,
    latest_version,
]
