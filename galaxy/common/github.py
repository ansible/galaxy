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

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.github.provider import GitHubProvider

provider_id = GitHubProvider.id
settings = app_settings.PROVIDERS.get(provider_id, {})


def get_github_web_url():
    if 'GITHUB_URL' in settings:
        return settings.get('GITHUB_URL').rstrip('/')
    else:
        return 'https://github.com'


def get_github_api_url():
    if 'GITHUB_URL' in settings:
        return '{0}/api/v3'.format(get_github_web_url())
    else:
        return 'https://api.github.com'
