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

from django.urls import path

from galaxy.api.v2 import views

app_name = 'api'
urlpatterns = [
    # Collection URLs
    path('collections/',
         views.CollectionListView.as_view(),
         name='collections-list'),
    path('collections/<namespace>/<name>/versions/<version>/artifact/',
         views.CollectionArtifactView.as_view(),
         name='collection-version-artifact'),

    # Collection Imports URLs
    path('collection-imports/<int:pk>/',
         views.CollectionImportView.as_view(),
         name='collection-import-detail'),

    # Collection Versions URLs
    path('collection-versions/<int:pk>/',
         views.CollectionVersionView.as_view(),
         name='collection-version-detail'),
    path('collection-versions/<int:pk>/artifact/',
         views.CollectionArtifactView.as_view(),
         name='collection-version-artifact')
]
