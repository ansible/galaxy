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

from django.forms import ModelForm, CharField, ValidationError
from django.utils.html import mark_safe

from models import Role

class RoleForm(ModelForm):
    name = CharField(required=False)
    
    class Meta:
        model = Role
        fields = ('github_user','github_repo','name')

    def clean(self):
        regex = re.compile(r'^(ansible[-_.+]*)*(role[-_.+]*)*')

        # github only allows alphanumerics plus a dash for user names
        username_re = re.compile(r"^[0-9A-Za-z\-]+$")
        # repos can also have underscores, which we'll also allow
        # for with the alternate (optional) name specified 
        reponame_re = re.compile(r"^[0-9A-Za-z\-\._]+$")
        
        cleaned_data = super(RoleForm, self).clean()
        github_user = cleaned_data.get("github_user","")
        github_repo = cleaned_data.get("github_repo","")
        name        = cleaned_data.get("name","") or github_repo

        # cleanup the data a bit
        github_user = github_user.strip()
        github_repo = github_repo.strip()
        
        # we don't allow periods in the repo name, to prevent issues
        # like user.name.repo.name
        name = name.strip().replace(".", "_")
        
        if not name in ['ansible','Ansible']:
            # Remove undesirable substrings
            name = regex.sub('', name)


        # then do some basic validation
        if github_user == "":
            self._errors["github_user"] = self.error_class(["The github user field cannot be left blank."])
        elif not username_re.search(github_user):
            self._errors["github_user"] = self.error_class([
                                              "The github user field contains invalid characters. "
                                              "Please use alphanumeric characters and dashes only."
                                          ])
        if github_repo == "":
            self._errors["github_repo"] = self.error_class(["The github repo field cannot be left blank."])
        elif not reponame_re.search(github_repo):
            self._errors["github_repo"] = self.error_class([
                                              "The github repo field contains invalid characters. "
                                              "Please use alphanumeric characters, dashes and underscores only."
                                          ])
        if name == "":
            self.add_error(None, mark_safe('Empty name encountered.'
                '<p style="padding-top:10px;"><strong>NOTE:</strong> When determining '
                'the role name, <em>(ansible[-_.+]*)*(role[-_.+]*)*</em> is stripped from the '
                'beginning of the name.</p>'
                '<p>For example, the name <em>ansible-role-ansible</em> results in a role name of '
                '<em>ansible</em>. Both <em>ansible-role</em> and <em>ansible-ansible</em> result '
                'in an empty string, which is not valid.</p>'))
        elif not reponame_re.search(name):
            self._errors["name"] = self.error_class([
                                       "The name field contains invalid characters. "
                                       "Please use alphanumeric characters, dashes and underscores only."
                                   ])

        # reset the cleaned data values to the sanitized ones
        cleaned_data["github_user"] = github_user
        cleaned_data["github_repo"] = github_repo
        cleaned_data["name"] = name

        # Always return the full collection of cleaned data.
        return cleaned_data
