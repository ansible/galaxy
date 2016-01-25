# 
#  throttling.py
#   
#  (c) 2012-2015, Ansible, Inc.
#   

import re
import logging

from django.core.cache import caches
from rest_framework.throttling import ScopedRateThrottle
from galaxy.main.models import Role

class RoleDownloadCountThrottle(ScopedRateThrottle):
    cache = caches['download_count']
    role_id = None

    def __init__(self):
        return super(RoleDownloadCountThrottle, self).__init__()

    def allow_request (self, request, view):
        logger = logging.getLogger(__name__)
        logger.debug('RoleDownloadCountThrottle:')
        if (request.query_params.get('owner__username', None) or request.query_params.get('namespace', None)) and request.query_params.get('name', None):
            # this is a download request
            if request.query_params.get('owner__username', None):
                role_namespace = request.query_params['owner__username']
            else:
                role_namespace = request.query_params['namespace']
            role_name = request.query_params['name']
            try:
                # attempt to lookup role first. if that fails, we don't want get_cache_key to be called.
                role = Role.objects.get(namespace=role_namespace,name=role_name)
                self.role_id = role.id
                allowed = super(RoleDownloadCountThrottle, self).allow_request(request, view)
                if not allowed:
                    # user downloaded requested role already
                    logger.debug('user requested role %s.%s already.' % (role_namespace,role_name))
                    return True
                role.download_count += 1
                role.save()
            except:
                print 'Failed to find role %s.%s' % (role_namespace, role_name)
        return True

    def get_cache_key(self, request, view):
        """
        Generate a unique cache key by concatenating the user id
        with the '.throttle_scope` and the primary key of the request
        """
        logger = logging.getLogger(__name__)
        ident = self.get_ident(request)
        logger.debug("RoleDownloadCountThrottle cache key: %s_%s_%s" % (self.scope,ident,self.role_id))
        return self.cache_format % {
            'scope': self.scope,
            'ident': "%s_%s" % (ident, self.role_id)
        }