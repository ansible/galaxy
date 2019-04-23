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
from django import shortcuts

from galaxy.api import base
from galaxy.api.internal import serializers
from galaxy.main import models


class CollectionList(base.ListAPIView):
    model = models.Collection
    serializer_class = serializers.CollectionListSerializer
    queryset = models.Collection.objects.all()


class CollectionDetail(base.RetrieveAPIView):
    model = models.Collection
    serializer_class = serializers.CollectionDetailSerializer

    def get_object(self):
        return shortcuts.get_object_or_404(self.model, **self.kwargs)
