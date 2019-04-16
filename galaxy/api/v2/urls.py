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

    # Collection Imports URLs
    path('collection-imports/<int:pk>/',
         views.CollectionImportView.as_view(),
         name='collection-import-detail'),

    # Collection Version detail URLs
    path('collection-versions/<int:version_pk>/',
         views.VersionDetailView.as_view(),
         name='version-detail-by-id'),
    path('collections/<str:namespace>/<str:name>/versions/<str:version>/',
         views.VersionDetailView.as_view(),
         name='version-detail-by-collection-and-version-name'),

    # Artifact download URLs
    path('collection-versions/<int:pk>/artifact/',
         views.CollectionArtifactView.as_view(),
         name='collection-version-artifact'),
    path('collections/<namespace>/<name>/versions/<version>/artifact/',
         views.CollectionArtifactView.as_view(),
         name='collection-version-artifact'),

    # Collection Version list URLs
    path('collections/<int:pk>/versions/',
         views.VersionListView.as_view(),
         name='version-list-by-collection-id'),
    path('collections/<str:namespace>/<str:name>/versions/',
         views.VersionListView.as_view(),
         name='version-list-by-collection-name'),

    # Collection URLs
    path('collections/',
         views.CollectionListView.as_view(),
         name='collection-list'),
    path('collections/<int:pk>/',
         views.CollectionDetailView.as_view(),
         name='collection-detail-by-id'),
    # NOTE: needs to come after 'collections/<int:collection_pk>/versions/'
    path('collections/<str:namespace>/<str:name>/',
         views.CollectionDetailView.as_view(),
         name='collection-detail-by-name'),
]
