# (c) 2012-2019, Ansible by Red Hat
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

from rest_framework import exceptions as drf_exc
from rest_framework import serializers

from galaxy.common.schema import CollectionFilename


__all__ = (
    'CollectionUploadSerializer',
)


class CollectionUploadSerializer(serializers.Serializer):

    file = serializers.FileField(
        help_text="The collection file.",
        required=True,
    )

    sha256 = serializers.CharField(
        required=False,
        default=None,
    )

    def validate(self, data):
        super().validate(data)

        try:
            data['filename'] = CollectionFilename.parse(
                data['file'].name)
        except ValueError as e:
            raise drf_exc.ValidationError(str(e))

        return data
