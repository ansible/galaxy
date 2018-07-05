from ansiblelint import AnsibleLintRule


class MetaMainHasInfoRule(AnsibleLintRule):
    id = 'EXTRA0013'
    shortdesc = 'meta/main.yml should contain relevant info'
    info = ['author', 'description', 'company',
            'min_ansible_version', 'platforms', 'license']
    description = 'meta/main.yml should contain: ' + ', '.join(info)
    tags = ['role']

    def matchplay(self, file, data):
        results = []
        if 'galaxy_info' not in data:
            return [({'meta/main.yml': data}, self.description)]
        for info in self.info:
            if not data['galaxy_info'].get(info, None):
                results.append(({'meta/main.yml': data},
                                'role info should contain %s' % info))
        return results
