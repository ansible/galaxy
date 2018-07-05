from ansiblelint import AnsibleLintRule
import re


class ComparisonToLiteralBoolRule(AnsibleLintRule):
    id = 'EXTRA0014'
    shortdesc = "Don't compare to literal True/False"
    description = 'Use `when: var` rather than `when: var == True` ' \
                  '(or conversely `when: not var`)'
    tags = ['idiom']
    literal_bool_compare = re.compile("[=!]= ?(True|true|False|false)")

    def match(self, file, line):
        return self.literal_bool_compare.search(line)
