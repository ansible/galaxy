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

import logging

from django.core.cache import caches
from rest_framework.throttling import ScopedRateThrottle
from galaxy.main.models import Content


class RoleDownloadCountThrottle(ScopedRateThrottle):
    cache = caches['download_count']
    role_id = None

    def __init__(self):
        self.role_id = None
        self.logger = logging.getLogger(__name__)
        super(RoleDownloadCountThrottle, self).__init__()

    def allow_request(self, request, view):
        self.logger.debug('RoleDownloadCountThrottle:')
        if (request.query_params.get('owner__username')
                or request.query_params.get('namespace')
                and request.query_params.get('name')):
            # this is a download request
            if request.query_params.get('owner__username', None):
                role_namespace = request.query_params['owner__username']
            else:
                role_namespace = request.query_params['namespace']
            role_name = request.query_params['name']
            try:
                # attempt to lookup role first. if that fails,
                # we don't want get_cache_key to be called.
                role = Content.objects.get(namespace=role_namespace,
                                           name=role_name)
                self.role_id = role.id
                allowed = super(RoleDownloadCountThrottle, self).allow_request(
                    request, view)
                if not allowed:
                    # user downloaded requested role already
                    self.logger.debug(
                        'user requested role {}.{} already.'.format(
                            role_namespace, role_name))
                    return True
                role.download_count += 1
                role.save()
            except Exception as e:
                self.logger.error(
                    'Error finding role {}.{} - {}'.format(
                        role_namespace, role_name, str(e.args)))
        return True

    def get_cache_key(self, request, view):
        """
        Generate a unique cache key by concatenating the user id
        with the '.throttle_scope` and the primary key of the request
        """
        ident = self.get_ident(request)
        self.logger.debug(
            "RoleDownloadCountThrottle cache key: {}_{}_{}".format(
                self.scope, ident, self.role_id))
        return self.cache_format % {
            'scope': self.scope,
            'ident': "%s_%s" % (ident, self.role_id)
        }
