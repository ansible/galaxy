#!/usr/bin/env python

import re
import subprocess

author_re = re.compile(r'^\s*\d+\t([\w ]+ <[^>]+>)$')

git_log = subprocess.check_output(['git', 'shortlog', '--summary', '--email'])
log_entries = git_log.decode('utf-8').strip().split('\n')
authors = [author_re.match(entry).group(1) for entry in log_entries]


print("Galaxy has been contribued to by the following authors:\n"
      "This list is automatically generated - please file an issue for corrections)\n")
for author in authors:
    print(author)
