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

from __future__ import absolute_import

import os
import logging

from galaxy.importer.models import CollectionArtifactManifest, Collection
from galaxy.importer.utils import readme as readmeutils
from galaxy.importer import finders as finders_
from galaxy.importer import loaders
from galaxy.importer import exceptions as exc


default_logger = logging.getLogger(__name__)


def import_collection(directory, logger=None):
    logger = logger or default_logger
    return CollectionLoader(directory, logger=logger).load()


class CollectionLoader(object):
    """Loads collection and content info."""

    finders = [
        finders_.FileSystemFinder,
    ]

    def __init__(self, path, logger=None):
        self.log = logger or default_logger
        self.path = path

        self.collection_info = None
        self.contents = None
        self.readme = None

    def load(self):
        self._load_collection_manifest()
        self._load_collection_readme()

        finder, content_list = self._find_contents()
        self.contents = list(self._load_contents(content_list))

        quality_score = self._get_collection_quality_score()

        return Collection(
            collection_info=self.collection_info,
            contents=self.contents,
            readme=self.readme,
            quality_score=quality_score,
        )

    def _load_collection_manifest(self):
        manifest_file = os.path.join(self.path, 'MANIFEST.json')
        if not os.path.exists(manifest_file):
            raise exc.ManifestNotFound('No manifest found in collection')

        with open(manifest_file, 'r') as f:
            try:
                meta = CollectionArtifactManifest.parse(f.read())
            except ValueError as e:
                raise exc.ManifestValidationError(str(e))
            self.collection_info = meta.collection_info

    def _load_collection_readme(self):
        if not self.collection_info.readme:
            raise exc.ManifestValidationError(
                'No readme listed in manifest')

        readme_file = os.path.join(self.path,
                                   self.collection_info.readme)

        _, extension = os.path.splitext(readme_file)
        if extension not in ('.md', '.rst'):
            raise exc.ManifestValidationError(
                'Readme must be .md or .rst')

        try:
            self.readme = readmeutils.get_readme(
                directory=self.path,
                filename=readme_file)
        except readmeutils.FileSizeError as e:
            raise exc.ManifestValidationError(
                'Manifest readme FileSizeError: {}'.format(e))

        if not self.readme:
            raise exc.ManifestValidationError(
                'Readme listed in manifest not found: '
                '{}'.format(self.collection_info.readme))

    def _find_contents(self):
        for finder_cls in self.finders:
            try:
                finder = finder_cls(self.path, self.log)
                contents = finder.find_contents()
                return finder, contents
            except exc.ContentNotFound:
                pass
        raise exc.ContentNotFound("No content found in collection")

    def _load_contents(self, content_list):
        for content_type, rel_path, extra in content_list:
            loader_cls = loaders.get_loader(content_type)
            loader = loader_cls(content_type, rel_path, self.path,
                                logger=self.log, **extra)

            self.log.info('===== LOADING {} ====='.format(
                          content_type.name))
            content = loader.load()
            self.log.info(' ')

            name = ': {}'.format(content.name) if content.name else ''
            self.log.info('===== LINTING {}{} ====='.format(
                          content_type.name, name))
            loader.lint()
            content.scores = loader.score()
            self.log.info(' ')
            self.log.info('===== IMPORTING {}{} ====='.format(
                          content_type.name, name))
            self.log.info(' ')

            yield content

    def _get_collection_quality_score(self):
        coll_points = 0.0
        count = 0
        for content in self.contents:
            if content.scores:
                coll_points += content.scores['quality']
                count += 1
        quality_score = None if count == 0 else coll_points / count
        return quality_score
