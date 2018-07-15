from ansiblelint import AnsibleLintRule


class DontUseLineinfileRule(AnsibleLintRule):
    id = 'EXTRA0002'
    shortdesc = 'The lineinfile module is typically nasty'
    description = 'While lineinfile supports some idemptotency, using ' \
                  'template or assemble modules to populate configuration ' \
                  'files is preferred'
    tags = ['leastsurprise']

    def matchtask(self, file, task):
        return task["action"]["__ansible_module__"] == 'lineinfile'
