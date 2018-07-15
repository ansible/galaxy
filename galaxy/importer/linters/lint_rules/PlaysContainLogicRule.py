from ansiblelint import AnsibleLintRule


class PlaysContainLogicRule(AnsibleLintRule):
    id = 'EXTRA0008'
    shortdesc = 'plays should not contain logic'
    description = 'plays should not contain tasks, handlers or vars'
    tags = ['dry']

    def matchplay(self, file, play):
        results = []
        for logic in ['tasks', 'pre_tasks', 'post_tasks', 'vars', 'handlers']:
            if logic in play and play[logic]:
                # we can only access line number of first thing in the section
                # so we guess the section starts on the line above.
                results.append(({file['type']: play},
                                "%s should not be required in a play" % logic))
        return results
