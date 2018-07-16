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

import os
import errno
import collections
import contextlib
import tempfile
import shutil
import subprocess

import dateutil.parser as dt_parser


TIMEOUT_RETCODE = 124


class RepositoryNotExist(Exception):
    """Repository does not exist exception."""

    pass


@contextlib.contextmanager
def make_clone_dir(basedir=None):
    """
    Creates temporary directory and deletes at the end.

    Temporary directory may be deleted by `git clone` if clone failed with
    error.

    :param str basedir: Base directory to create temporary dir in.
    :rtype: str
    :return: Temporary directory path.
    :raises OSError:  If failed to remove a file or directory.
    """
    path = tempfile.mkdtemp(dir=basedir)
    try:
        yield path
    finally:
        try:
            shutil.rmtree(path)
        except OSError as e:
            # Note(cutwater): Suppress exception if directory
            # has been deleted already.
            if e.errno != errno.ENOENT:
                raise


def clone_repository(clone_url, directory, branch=None):
    """
    Clones a git repository to destination directory.

    :param str clone_url: The repository URL to clone from.
    :param str directory: The name of a directory to clone into.
    :param str branch: Branch name to checkout. If not specified,
        a default branch is checked out.
    :raises subprocess.CalledProcessError: If git command finished with
        non-zero exit code.
    :raises RepositoryNotExist: If repository does not exist.
    """
    # NOTE: Checking that remote repository exists. If trying to clone
    # without this check `git clone` will hang on waiting for
    # authentication user input.
    # This code should be removed once git version is upgrade.
    # Starting from version 2.3 git provides GIT_TERMINAL_PROMPT environment
    # variable, that causes immediate exit of `git clone` command.
    cmd = ['timeout', '10', 'git', 'ls-remote', clone_url]
    with open(os.devnull, 'w') as null_file:
        try:
            subprocess.check_call(cmd, stdout=null_file)
        except subprocess.CalledProcessError as e:
            if e.returncode == TIMEOUT_RETCODE:
                raise RepositoryNotExist("Repository '{0}' does not exist"
                                         .format(clone_url))
            else:
                raise

        cmd = ['git', 'clone', '--quiet', '--depth', '1']
        if branch:
            cmd += ['--branch', branch]
        cmd += [clone_url, directory]
        subprocess.check_call(cmd, stdout=null_file)


def get_current_branch(directory=None):
    """
    Returns branch name referenced by HEAD.

    :param str directory: Repository directory.
    :returns: Branch name if HEAD refers to branch.
    :rtype: str
    :raises subprocess.CalledProcessError: If git command finished with
        non-zero exit code.
    """
    cmd = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
    return subprocess.check_output(cmd, cwd=directory).strip()


# See `git help log` for details
_LOG_FORMAT = [
    ('sha', '%H'),
    ('author', '%an'),
    ('author_email', '%ae'),
    ('author_date', '%ad'),
    ('committer', '%cn'),
    ('committer_email', '%ce'),
    ('committer_date', '%cd'),
    ('message', '%B'),
]

CommitInfo = collections.namedtuple(
    'CommitInfo', (v[0] for v in _LOG_FORMAT))


def get_raw_commit_info(commit_id='HEAD', directory=None, date_format=None):
    """
    Returns metadata for the specified commit.

    :param commit_id: Commit id, by default HEAD is used.
    :param directory: Repository directory.
    :param date_format: Date format. Valid values are:
        relative, local, iso, iso-strict, rfc, short, raw, unix,
        format:...
    :returns: Commit metadata (e.g. sha, author, comitter, message, etc.)
    :rtype: dict
    """
    log_format = '%x1f'.join(v[1] for v in _LOG_FORMAT)

    cmd = ['git', 'log', '-1', '--format=' + log_format]
    if date_format:
        cmd.append('--date=' + date_format)
    cmd.append(commit_id)

    values = subprocess.check_output(cmd, cwd=directory).strip().split('\x1f')
    return dict(zip((v[0] for v in _LOG_FORMAT), values))


def get_commit_info(commit_id='HEAD', directory=None):
    """
    Returns metadata for the specified commit.

    :returns: Commit metadata (e.g. sha, author, comitter, message, etc.)
    :rtype: CommitInfo
    """
    ci = get_raw_commit_info(commit_id, directory, date_format='iso')
    ci['author_date'] = dt_parser.parse(ci['author_date'])
    ci['committer_date'] = dt_parser.parse(
        ci['committer_date'])
    return CommitInfo(**ci)
