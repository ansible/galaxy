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

# django libs

from django.contrib import admin

# local stuff

from galaxy.main.models import *

###################################################################################
# Admin Models

class PlatformAdmin(admin.ModelAdmin):
    pass
admin.site.register(Platform, PlatformAdmin)

class RoleAdmin(admin.ModelAdmin):
    pass
admin.site.register(Role, RoleAdmin)

class RoleVersionAdmin(admin.ModelAdmin):
    pass
admin.site.register(RoleVersion, RoleVersionAdmin)

#class RoleImportAdmin(admin.ModelAdmin):
#    pass
#admin.site.register(RoleImport, RoleImportAdmin)

class RoleRatingAdmin(admin.ModelAdmin):
    pass
admin.site.register(RoleRating, RoleRatingAdmin)

class CategoryAdmin(admin.ModelAdmin):
    pass
admin.site.register(Category, CategoryAdmin)

class UserAliasAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserAlias, UserAliasAdmin)
