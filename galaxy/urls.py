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

from django.conf.urls import patterns, include, url
from django.contrib import admin
import autofixture

admin.autodiscover()
autofixture.autodiscover()

urlpatterns = patterns('',
  url(r'', include('galaxy.main.urls', namespace='main', app_name='main')),
  url(r'^accounts/', include('allauth.urls')),
  url(r'^api/', include('galaxy.api.urls', namespace='api', app_name='api')),
  url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
  url(r'^avatar/', include('avatar.urls')),
  url(r'^galaxy__admin/', include(admin.site.urls)),
)

