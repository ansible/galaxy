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

import collections

import marshmallow as mm
from marshmallow import fields
from marshmallow import validate

from galaxy import constants
from galaxy.common import schema
from galaxy.importer.utils import git

SHA1_LEN = 40


# ---------------------------------------------------------

PlatformInfo = collections.namedtuple(
    'PlatformInfo', ['name', 'versions'])
DependencyInfo = collections.namedtuple(
    'DependencyInfo', ['namespace', 'name'])
VideoLink = collections.namedtuple(
    'VideoLink', ['url', 'description'])


class Content(object):
    """Represents common content data."""

    def __init__(self, name, path, content_type,
                 description='', role_meta=None,
                 metadata=None):
        self.name = name
        self.path = path
        self.content_type = content_type
        self.description = description
        self.role_meta = role_meta
        self.metadata = metadata or {}


class Repository(object):
    """Represents repository metadata."""
    def __init__(self, branch, commit, format, contents):
        self.branch = branch
        self.commit = commit
        self.format = format
        self.contents = contents


# -----------------------------------------------------------------------------


class PlatformInfoSchema(mm.Schema):
    name = fields.Str()
    versions = fields.List(fields.Str)

    @mm.post_load
    def make_object(self, data):
        return PlatformInfo(**data)


class DependencyInfoSchema(mm.Schema):
    namespace = fields.Str()
    name = fields.Str()

    @mm.post_load
    def make_object(self, data):
        return DependencyInfo(**data)


class VideoLinkSchema(mm.Schema):
    url = fields.Str()
    description = fields.Str()

    @mm.post_load
    def make_object(self, data):
        return VideoLink(**data)


class CommitInfoSchema(mm.Schema):
    """A schema for CommitInfo class."""
    sha = fields.Str(validate=validate.Length(equal=SHA1_LEN))
    author = fields.Str()
    author_email = fields.Str()
    author_date = fields.DateTime()
    committer = fields.Str()
    committer_email = fields.Str()
    committer_date = fields.DateTime()
    message = fields.Str()

    @mm.post_load
    def make_object(self, data):
        return git.CommitInfo(**data)


class RoleMetaSchema(mm.Schema):
    author = fields.Str()
    company = fields.Str()
    license = fields.Str()
    min_ansible_version = fields.Str(allow_none=True)
    min_ansible_container_version = fields.Str(allow_none=True)
    issue_tracker = fields.Str()
    github_branch = fields.Str()

    role_type = schema.Enum(constants.RoleType)
    tags = fields.List(fields.Str)
    platforms = fields.Nested(PlatformInfoSchema(), many=True)
    cloud_platforms = fields.List(fields.Str)
    dependencies = fields.Nested(DependencyInfoSchema(), many=True)
    video_links = fields.Nested(VideoLinkSchema(), many=True)


class ContentSchema(mm.Schema):
    """A schema for Content class."""
    name = fields.Str()
    path = fields.Str()
    content_type = schema.Enum(constants.ContentType)
    description = fields.Str()
    # Note(cutwater): This is workaround to make properly serializable
    # role metadata.
    role_meta = fields.Nested(RoleMetaSchema())
    metadata = fields.Dict()

    @mm.post_load
    def make_object(self, data):
        return Content(**data)


class RepositorySchema(mm.Schema):
    """A schema for Repository class."""
    branch = fields.Str()
    commit = fields.Nested(CommitInfoSchema())
    format = schema.Enum(constants.RepositoryFormat)
    contents = fields.Nested(ContentSchema(), many=True)

    @mm.post_load
    def make_object(self, data):
        return RepositorySchema(**data)
