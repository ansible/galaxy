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

"""
Based on code found at:
http://russellneufeld.wordpress.com/2012/05/24/using-memcached-as-a-distributed-lock-from-within-django/

We use this primarily from celery tasks to ensure that 
background calculations do not step on each other. In order
to get around some of the issues presented at the above
link, instead of monkey patching the memcache backend we 
instead use a distributed/replicated store like couchbase.
This allows us to guarantee that 
"""

import time
import logging
import contextlib
import random
from django.core.cache import cache as django_cache
 
class MemcacheLockException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
 
@contextlib.contextmanager
def memcache_lock(key, attempts=1, expires=120):
    key = '__d_lock_%s' % key
 
    got_lock = False
    try:
        got_lock = _acquire_lock(key, attempts, expires)
        yield
    finally:
        if got_lock:
            _release_lock(key)
 
def _acquire_lock(key, attempts, expires):
    for i in xrange(0, attempts):
        stored = django_cache.add(key, 1, expires)
        if stored:
            return True
        if i != attempts-1:
            sleep_time = (((i+1)*random.random()) + 2**i) / 2.5
            logging.debug('Sleeping for %s while trying to acquire key %s', sleep_time, key)
            time.sleep(sleep_time)
    raise MemcacheLockException('Could not acquire lock for %s' % key)
 
def _release_lock(key):
    django_cache.delete(key)
