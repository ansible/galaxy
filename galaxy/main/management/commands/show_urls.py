# (c) 2012-2016, Ansible by Red Hat
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
from django.core import urlresolvers
from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        resolver = urlresolvers.get_resolver(None)
        for url_path, url in sorted(
                self._iter_urls(resolver), key=lambda x: x[0]):
            callback_path = '{0}.{1}'.format(
                url.callback.__module__, url.callback.__name__)
            print('{0:60} {1}'.format(url_path, callback_path))

    @staticmethod
    def _iter_urls(resolver):
        resolvers = [('/', resolver)]
        while resolvers:
            prefix, resolver = resolvers.pop()
            for url in resolver.url_patterns:
                url_path = prefix + url.regex.pattern.lstrip('^').rstrip('$')
                if isinstance(url, urlresolvers.RegexURLResolver):
                    resolvers.append((url_path, url))
                elif isinstance(url, urlresolvers.RegexURLPattern):
                    yield url_path, url
