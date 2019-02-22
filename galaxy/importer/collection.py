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
import tempfile
import tarfile
import shutil
import logging

from galaxy.importer.models import CollectionArtifactManifest, Collection
from galaxy.importer.utils import readme as readmeutils
from galaxy.importer import finders as finders_
from galaxy.importer import loaders
from galaxy.importer import exceptions as exc


default_logger = logging.getLogger(__name__)


def import_collection(artifact, logger=None):
    logger = logger or default_logger
    with tempfile.TemporaryDirectory() as temp_dir:
        return CollectionLoader(artifact, temp_dir, logger=logger).load()


class CollectionLoader(object):
    """Loads collection and content info."""

    finders = [
        finders_.FileSystemFinder,
    ]

    def __init__(self, artifact, temp_dir, logger=None):
        self.log = logger or default_logger
        self.artifact = artifact
        self.temp_dir = temp_dir
        self.artifact_path = None
        self.collection_path = None
        self.collection_info = None
        self.contents = None
        self.readme = None

    def load(self):
        self._extract_package()
        self._load_collection_manifest()
        self._load_collection_readme()

        finder, content_list = self._find_contents()
        self.contents = list(self._load_contents(content_list))

        self._validate_collection_metadata()

        quality_score = self._get_collection_quality_score()

        return Collection(
            collection_info=self.collection_info,
            contents=self.contents,
            readme=self.readme,
            quality_score=quality_score,
        )

    def _extract_package(self):
        self.artifact_path = os.path.join(
            self.temp_dir,
            os.path.basename(self.artifact.file.path))
        shutil.copy(self.artifact.file.path, self.artifact_path)

        with tarfile.open(self.artifact_path, 'r') as pkg:
            pkg.extractall(self.temp_dir)

        _, dirs, _ = next(os.walk(self.temp_dir))
        self.collection_path = os.path.join(self.temp_dir, dirs[0])
        self.log.info('Extracting collection: {}'.format(dirs[0]))
        self.log.info(' ')

    def _load_collection_manifest(self):
        with tarfile.open(self.artifact_path, 'r') as pkg:
            for member in pkg.getmembers():
                if member.isfile() and \
                        member.path.split('/')[-1] == 'MANIFEST.json':
                    manifest = member
                    break
            if not manifest:
                raise exc.ManifestNotFound('No manifest found in collection')

            meta_file = pkg.extractfile(manifest)
            with meta_file:
                meta = CollectionArtifactManifest.parse(meta_file.read())
                self.collection_info = meta.collection_info

    def _load_collection_readme(self):
        try:
            self.readme = readmeutils.get_readme(
                directory=self.collection_path)
        except readmeutils.FileSizeError as e:
            self.log.warning(e)

    def _validate_collection_metadata(self):
        pass

    def _find_contents(self):
        for finder_cls in self.finders:
            try:
                finder = finder_cls(self.collection_path, self.log)
                contents = finder.find_contents()
                return finder, contents
            except exc.ContentNotFound:
                pass
        raise exc.ContentNotFound("No content found in collection")

    def _load_contents(self, content_list):
        for content_type, rel_path, extra in content_list:
            loader_cls = loaders.get_loader(content_type)
            loader = loader_cls(content_type, rel_path, self.collection_path,
                                logger=self.log, **extra)

            self.log.info('===== LOADING {} ====='.format(
                          content_type.name))
            content = loader.load()
            self.log.info(' ')

            name = ': {}'.format(content.name) if content.name else ''
            self.log.info('===== LINTING {}{} ====='.format(
                          content_type.name, name))
            loader.lint()
            # content.scores = loader.score()
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
