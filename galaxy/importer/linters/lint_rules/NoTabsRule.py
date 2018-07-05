from ansiblelint import AnsibleLintRule


class NoTabsRule(AnsibleLintRule):
    id = 'EXTRA0005'
    shortdesc = 'Most files should not contain tabs'
    description = 'Tabs can cause unexpected display issues. Use spaces'
    tags = ['whitespace']

    def match(self, file, line):
        return '\t' in line
