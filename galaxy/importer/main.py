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

import argparse

from . import repository
from . import models


def import_repository(url, output=None, branch=None):
    """Imports repository and serializes

    :param url: Remote repository URL.
    :param ouptut: Output file to write import results.
    :param branch: Clone branch. If not set the default repository branch
        will be used.
    """
    data = repository.import_repository(url, branch=branch)
    result = models.RepositorySchema(strict=True).dumps(data)
    with open(output, 'wb') as fp:
        fp.write(result)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Import repository and run linting')

    parser.add_argument(
        '-b', '--branch', default=None, help='Branch to clone.')
    parser.add_argument(
        '-o', '--output',
        help='Output file to write import results in YAML format.')
    parser.add_argument(
        'url', help='A remote repository URL to clone from.')

    return parser.parse_args(args=args)


def main(args=None):
    args = parse_args(args)

    import_repository(url=args.url,
                      output=args.output,
                      branch=args.branch)


if __name__ == '__main__':
    exit(main())
