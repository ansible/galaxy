from ansiblelint import AnsibleLintRule


class DontDelegateToLocalhostRule(AnsibleLintRule):
    id = 'EXTRA0004'
    shortdesc = 'Use connection: local rather than delegate_to: localhost'
    description = 'Connection: local ensures that unexpected delegated_vars ' \
                  "don't get set (e.g. {{ inventory_hostname }} " \
                  "used by vars_files)"
    tags = ['leastsurprise']

    def matchtask(self, file, task):
        return task.get('delegate_to') == 'localhost'
