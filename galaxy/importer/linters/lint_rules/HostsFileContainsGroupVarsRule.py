from ansiblelint import AnsibleLintRule


class HostsFileContainsGroupVarsRule(AnsibleLintRule):
    id = 'EXTRA0009'
    shortdesc = 'hosts files should not contain group vars'
    description = 'Use inventory group_vars directory rather than ' \
                  '[group:vars] in hosts file'
    tags = ['inventory']

    def match(self, file, line):
        return line.startswith('[') and line.endswith(':vars]')
