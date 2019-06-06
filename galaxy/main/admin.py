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

from django.contrib import admin
from galaxy.main import models


@admin.register(models.Platform)
class PlatformAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CloudPlatform)
class CloudPlatformAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.RepositoryVersion)
class RepositoryVersionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name', )


@admin.register(models.Namespace)
class NamespaceAdmin(admin.ModelAdmin):
    autocomplete_fields = ('owners', )


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    exclude = ('search_vector', )
    autocomplete_fields = ('tags', )
