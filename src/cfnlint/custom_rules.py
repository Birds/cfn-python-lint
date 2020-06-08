"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
# pylint: disable=W0108
# pylint: disable=W0622
import logging
import cfnlint
import cfnlint.runner
import cfnlint.customRules.Operators
import cfnlint.customRules.Rule

LOGGER = logging.getLogger(__name__)
Operator = {'EQUALS': lambda x, y: cfnlint.customRules.Operators.equalsOp(x, y),
            'PLACEHOLDER': lambda x, y: LOGGER.debug('Placeholder Op')}

def check(filename, template, rules, runner):
    """ Process custom rule file """
    matches = []
    with open(filename) as customRules:
        line_number = 1
        for line in customRules:
            LOGGER.debug('Processing Custom Rule Line %d', line_number)
            line = line.replace('"', '')
            rule = cfnlint.customRules.Rule.make_rule(line.split(' '))
            if rule.valid and rule.resourceType[0] != '#':
                try:
                    resource_properties = template.get_resource_properties([rule.resourceType])
                    result = Operator[rule.operator](rule, resource_properties)
                    if result.message != rule.operator:
                        matches.append(result)
                except KeyError:
                    matches.append(cfnlint.rules.Match(line_number, '0', '0', '0', filename, CustomRule('E9999'),
                                                       str(rule.operator) + ' not in supported operators: [EQUALS] at ' + str(line), None))
            line_number += 1
    arg_matches = []
    for match in matches:
        if rules.is_rule_enabled(match.rule.id, False):
            arg_matches.append(match)
    return runner.check_directives(arg_matches)

def match_helper(id):
    return cfnlint.rules.Match(1, '0', '0', '0', 'filename', CustomRule(id), 'result', None)

class CustomRule(object):
    """ Allows creation of match objects"""
    def __init__(self, id):
        self.id = id
