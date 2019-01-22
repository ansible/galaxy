import json
import re

import attr
import semantic_version as semver


_FILENAME_RE = re.compile(
    r'^(?P<namespace>\w+)-(?P<name>\w+)-'
    r'(?P<version>[0-9a-zA-Z.+-]+)\.tar\.gz$'
)
_NAME_RE = re.compile(r'^[0-9a-z_]+$')


@attr.s(slots=True)
class CollectionFilename(object):

    namespace = attr.ib()
    name = attr.ib()
    version = attr.ib(converter=semver.Version)

    @classmethod
    def parse(cls, filename):
        match = _FILENAME_RE.match(filename)
        if not match:
            raise ValueError(
                'Invalid filename. Expected: '
                '{namespace}-{name}-{version}.tar.gz'
            )

        return cls(**match.groupdict())

    @namespace.validator
    @name.validator
    def _validator(self, attribute, value):
        if not _NAME_RE.match(value):
            raise ValueError(
                'Invalid {0}: {1!r}'.format(attribute.name, value)
            )


@attr.s(frozen=True, slots=True, kw_only=True)
class Metadata:
    """Ansible Collection metadata."""
    namespace = attr.ib()
    name = attr.ib()
    version = attr.ib(converter=semver.Version)

    author = attr.ib(default='')
    author_email = attr.ib(default='')

    @name.validator
    @namespace.validator
    def _validate_name(self, attribute, value):
        if not _NAME_RE.match(value):
            raise ValueError('Invalid "{0}" attribute'.format(attribute))

    @classmethod
    def parse(cls, data):
        meta = json.loads(data)
        return cls(**meta)
