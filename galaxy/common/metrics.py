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
import sys

from django.conf import settings

from rest_framework.request import Request


__all__ = [
    'send',
]

logger = logging.getLogger(__name__)


def send(func_name):
    def decorator(function):
        def wrapper(*args, **kwargs):
            # call the view
            result = function(*args, **kwargs)

            if settings.METRICS_ENABLED:
                # TODO do this async
                _send(func_name, args[1])

            return result
        return wrapper
    return decorator


def _send(func_name, request):
    if not isinstance(request, Request):
        raise AssertionError(
            'Could not send metrics. '
            'Expected rest_framework.request.Request, got %s!'
            % type(request)
        )

    func = getattr(sys.modules[__name__], func_name, None)
    if not callable(func):
        raise AssertionError(
            'Could not send metrics. % is not callable!' % func_name
        )

    try:
        # FIXME POST?
        func(request.GET)
    except IOError as e:
        logger.exception(e)


def search(data):
    platforms = data.get('platforms', '').split()
    cloud_platforms = data.get('cloud_platforms', '').split()
    tags = data.get('tags', '').split()
    keywords = data.get('keywords', '').split()

    if not any((platforms, cloud_platforms, tags, keywords)):
        return

    search_criteria = {
        'keyword': keywords,
        'platform': platforms,
        'cloud_platform': cloud_platforms,
        'tag': tags,
    }

    settings.PROM_CNTR_SEARCH.labels(
        keywords=','.join(keywords),
        platforms=','.join(platforms),
        cloud_platforms=','.join(cloud_platforms),
        tags=','.join(tags)
    ).inc()

    for criteria_type, criteria_values in search_criteria.items():
        for criteria_value in criteria_values:
            settings.PROM_CNTR_SEARCH_CRITERIA.labels(
                ctype=criteria_type, cvalue=criteria_value).inc()
