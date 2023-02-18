#!/usr/bin/env python

import re
import subprocess

author_re = re.compile(r'(?<=\t).*')

git_log = subprocess.check_output(['git', 'shortlog', '--summary', '--email'])
log_entries = git_log.decode('utf-8').strip().split('\n')


print("Galaxy has been contribued to by the following authors:\n"
      "This list is automatically generated - please file an issue for corrections)\n")
for entry in log_entries:
    print(author_re.search(entry).group(0))
