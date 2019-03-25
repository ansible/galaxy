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

import semantic_version

from galaxy.main import models


class Context(object):
    def __init__(self, **kwargs):
        for arg, value in kwargs.items():
            setattr(self, arg, value)


def update_readme(repository, readme_obj, readme, github_api, github_repo):
    if readme_obj and readme and readme_obj.raw_hash == readme.hash:
        return readme_obj

    if readme_obj:
        readme_obj.safe_delete()

    if readme:
        readme_obj, created = models.Readme.objects.get_or_create(
            repository=repository, raw_hash=readme.hash,
            defaults={
                'raw': readme.text,
                'mimetype': readme.mimetype,
            }
        )
        if created:
            readme_obj.html = github_api.render_markdown(
                readme.text, context=github_repo)
            readme_obj.save()
        return readme_obj


def parse_version_tag(value):
    value = str(value)
    if not value:
        raise ValueError('Empty version value')
    if value[0].lower() == 'v':
        value = value[1:]
    return semantic_version.Version(value)
