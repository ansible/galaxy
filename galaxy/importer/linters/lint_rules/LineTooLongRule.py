from ansiblelint import AnsibleLintRule


class LineTooLongRule(AnsibleLintRule):
    id = 'EXTRA0006'
    shortdesc = 'Lines should be no longer than 100 chars'
    description = 'Long lines make code harder to read and ' \
                  'code review more difficult'
    tags = ['whitespace']

    def match(self, file, line):
        return len(line) > 100
