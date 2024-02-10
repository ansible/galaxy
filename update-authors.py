#!/usr/bin/env python

import re
import subprocess

author_re = re.compile(r'(?<=\t).*')

# Without the HEAD argument, git shortlog will fail when run during a pre-commit hook.
# Thanks to Michał Górny (https://stackoverflow.com/users/165333/micha%c5%82-g%c3%b3rny)
# for pointing this out: <https://stackoverflow.com/a/12133752/7593853>
git_log = subprocess.check_output(['git', 'shortlog', '--summary', '--email', 'HEAD'])
log_entries = git_log.decode('utf-8').strip().split('\n')


print("Galaxy has been contribued to by the following authors:\n"
      "This list is automatically generated - please file an issue for corrections)\n")
for entry in log_entries:
    print(author_re.search(entry).group(0))
