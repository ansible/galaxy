from ansiblelint import AnsibleLintRule


class HostIsLocalhostRule(AnsibleLintRule):
    id = 'EXTRA0007'
    shortdesc = 'use connection: local rather than host: localhost'
    description = 'Using hosts: localhost limits the quality of ' \
                  'variables available to your playbook'
    tags = ['dry']

    def matchplay(self, file, data):
        if data.get('hosts') == 'localhost':
            return [({file['type']: data}, self.shortdesc)]
