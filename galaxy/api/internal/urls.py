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

from django.urls import path, include
from galaxy.api.internal import views


ui_urls = [
    path('collections/', views.CollectionList.as_view()),
    path('collections/<int:pk>', views.CollectionUpdate.as_view()),
    path(
        'collections/<slug:namespace__name>/<slug:name>/',
        views.CollectionDetail.as_view()),
    path(
        'namespaces/<int:namespace_id>/imports/',
        views.NamespaceImportsList.as_view()),
    path('repos-and-collections/', views.RepoAndCollectionList.as_view()),
    path('repo-or-collection-detail/', views.CombinedDetail.as_view())
]


app_name = 'api'
urlpatterns = [
    path('ui/', include(ui_urls)),
]
