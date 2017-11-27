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

from django.contrib import admin
from galaxy.main import models


class PlatformAdmin(admin.ModelAdmin):
    pass


class CloudPlatformAdmin(admin.ModelAdmin):
    pass


class RoleAdmin(admin.ModelAdmin):
    pass


class RoleVersionAdmin(admin.ModelAdmin):
    pass


class ContentBlockAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Platform, PlatformAdmin)
admin.site.register(models.CloudPlatform, CloudPlatformAdmin)
admin.site.register(models.Role, RoleAdmin)
admin.site.register(models.RoleVersion, RoleVersionAdmin)
admin.site.register(models.ContentBlock, ContentBlockAdmin)
