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

import datetime as dt
import subprocess

import github
import requests
import pytz

from . import exceptions as exc

try:
    from tempfile import TemporaryDirectory
except ImportError:
    import contextlib
    import tempfile
    import shutil

    @contextlib.contextmanager
    def TemporaryDirectory(suffix="", prefix=tempfile.template, dir=None):
        path = tempfile.mkdtemp(suffix, prefix, dir)
        try:
            yield path
        finally:
            shutil.rmtree(path)


def clone_repository(clone_url, directory, branch=None):
    """Clones a git repository to destination directory.

    @param str clone_url: The repository URL to clone from.
    @param str directory: The name of a directory to clone into.
    @param str branch: Branch name to checkout. If not specified,
        a default branch is checked out.
    """
    cmd = ['git', 'clone', '--depth', '1']
    if branch:
        cmd += ['--branch', branch]
    cmd += [clone_url, directory]
    subprocess.check_call(cmd)


def get_commit_info(fields, commit_id=None, directory=None,
                    date_format=None):
    commit_id = commit_id or 'HEAD'
    log_format = '%x1f'.join(field[1] for field in fields)

    cmd = ['git', 'log', '-n', '1',
           '--format=' + log_format]
    if date_format:
        cmd.append('--date=' + date_format)
    cmd.append(commit_id)
    output = subprocess.check_output(cmd, cwd=directory).strip()

    return {fmt[0]: value.strip() for fmt, value
            in zip(fields, output.split('\x1f'))}


def parse_git_date_raw(date):
    return dt.datetime.fromtimestamp(
        int(date.strip().split(' ', 1)[0]), tz=pytz.utc)


def get_readme(token, repo):
    """
    Retrieve README from the repo and sanitize by removing all markup.

    Should preserve unicode characters.
    """
    try:
        readme = repo.get_readme()
    except github.UnknownObjectException:
        raise exc.WorkerError("Failed to get README file")
    readme_raw = readme.decoded_content

    if readme.name == 'README.md':
        file_type = 'md'
    elif readme.name == 'README.rst':
        file_type = 'rst'
    else:
        raise exc.WorkerError(
            u'Unable to determine README file type. '
            u'Expected file extensions: ".md", ".rst"')

    headers = {'Authorization': 'token %s' % token,
               'Accept': 'application/vnd.github.VERSION.html'}
    url = "https://api.github.com/repos/%s/readme" % repo.full_name
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    readme_html = response.text

    return readme_raw, readme_html, file_type


class Context(object):
    pass
