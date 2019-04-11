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
import hashlib
import mimetypes
import os

import markdown
import bleach
from bleach_whitelist import markdown_tags, markdown_attrs

README_NAME = 'README'
README_EXTENSIONS = [
    '',
    '.md',
    '.rst'
]
README_MIMETYPES = {
    '.md': 'text/markdown',
    '.rst': 'text/x-rst',
}
README_MAX_SIZE = 512 ** 2  # 512 KiB

ReadmeFile = collections.namedtuple(
    'ReadmeFile', ['text', 'mimetype', 'hash']
)

for _ext, _type in README_MIMETYPES.items():
    mimetypes.add_type(_type, _ext)


class FileSizeError(Exception):
    pass


def find_readme(directory):
    for ext in README_EXTENSIONS:
        filename = os.path.join(directory, README_NAME + ext)
        if os.path.exists(filename):
            return filename
    return None


def get_readme(directory, root_dir=None, filename=None):
    if not filename:
        filename = find_readme(directory)
        if not filename:
            return None
    elif not os.path.exists(filename):
        return None

    if os.path.getsize(filename) > README_MAX_SIZE:
        raise FileSizeError(
            'Readme file "{0}" is bigger than 512 KiB.'
            .format(os.path.relpath(filename, root_dir or directory)))

    mimetype, encoding = mimetypes.guess_type(filename)

    with open(filename, 'rb') as fp:
        raw_text = fp.read()
    hash_ = hashlib.sha256(raw_text).hexdigest()

    return ReadmeFile(
        text=raw_text.decode('utf-8'),
        mimetype=mimetype,
        hash=hash_
    )


def render_html(readme_file):
    html = ''
    if readme_file.mimetype == 'text/x-rst':
        pass
    elif readme_file.mimetype == 'text/markdown':
        unsafe_html = markdown.markdown(readme_file.text, extensions=['extra'])

        # note on bleach coming after markdown, and bleach_whitelist
        # https://github.com/Python-Markdown/markdown/issues/225
        html = bleach.clean(unsafe_html, tags=markdown_tags,
                            attributes=markdown_attrs, styles=[], strip=True)
    return html
