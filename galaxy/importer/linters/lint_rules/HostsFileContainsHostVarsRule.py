from ansiblelint import AnsibleLintRule
import re


class HostsFileContainsHostVarsRule(AnsibleLintRule):
    id = 'EXTRA0010'
    shortdesc = 'hosts files should not contain host vars'
    description = 'Use inventory host_vars directory rather than ' \
                  'host key=value in hosts file'
    tags = ['inventory']

    regex_host_var = re.compile('([^ ]+)=')

    def match(self, file, line):
        match = self.regex_host_var.search(line)
        if match:
            return any([not group.startswith("ansible_")
                        for group in match.groups()])
