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

from galaxy.main.models import Namespace
from .serializers import BaseSerializer


__all__ = [
    'NamespaceSerializer',
]


class NamespaceSerializer(BaseSerializer):

    class Meta:
        model = Namespace
        fields = (
            'id',
            'name',
            'description',
            'avatar_url',
            'location',
            'company',
            'email',
            'html_url',
        )

    def get_summary_fields(self, instance):
        owners = [{
            'id': u.id,
            'github_user': u.github_user,
            'github_avatar': u.github_avatar,
            'username': u.username
        } for u in instance.owners.all()]
        provider_namespaces = [{
            'id': pn.id,
            'name': pn.name,
            'display_name': pn.display_name,
            'avatar_url': pn.avatar_url,
            'location': pn.location,
            'compay': pn.company,
            'description': pn.description,
            'email': pn.email,
            'html_url': pn.html_url,
            'provider': pn.provider.id,
        } for pn in instance.provider_namespaces.all()]
        return {
            'owners': owners,
            'provider_namespaces': provider_namespaces
        }
