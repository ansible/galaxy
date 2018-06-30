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

from django.conf.urls import url
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.contrib.staticfiles.views import serve as serve_staticfiles
from django.views.static import serve as serve_static


urlpatterns = []

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', never_cache(serve_staticfiles))
    ]
else:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$',
            serve_static, kwargs={'document_root': settings.STATIC_ROOT}),
        url(r'^(?P<path>.*(?:css|js|png|jpg|jpeg|ico|woff|woff2|svg|ttf))/?$',
            serve_static, kwargs={'document_root': settings.STATIC_ROOT}),
        url(r'^(?!api|static|accounts|{})'.format(settings.ADMIN_URL_PATH),
            serve_static, kwargs={'document_root': settings.STATIC_ROOT,
                                  'path': 'index.html'})
    ]
