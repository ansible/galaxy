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

from galaxy.main import models
from galaxy.api import serializers

from . import base_views as base


__all__ = (
    'ContentBlockList',
    'ContentBlockDetail',
)


class ContentBlockList(base.ListAPIView):

    model = models.ContentBlock
    serializer_class = serializers.ContentBlockSerializer


class ContentBlockDetail(base.RetrieveAPIView):

    model = models.ContentBlock
    serializer_class = serializers.ContentBlockSerializer
    lookup_field = 'name'
