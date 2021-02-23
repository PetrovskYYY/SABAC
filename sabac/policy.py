#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Policy class

Object structure:
- target - dict
- description - text
- obligations
- advices
+ algorithm [
    DENY_OVERRIDES|PERMIT_OVERRIDES|
    DENY_UNLESS_PERMIT|PERMIT_UNLESS_DENY|
    FIRST_APPLICABLE|
    ORDERED_DENY_OVERRIDES|ORDERED_PERMIT_OVERRIDES
  ]
+ rules
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__version__ = "0.0.0"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"
__status__ = "dev"

# Standard library imports
import logging
# Local source imports
from .algorithm import *
from .rule import Rule
from .policy_element import PolicyElement
from .response import Response


class Policy(PolicyElement):
    def __init__(self, json_data=None, algorithm=None):
        self.rules = []
        PolicyElement.__init__(self, json_data, algorithm)

    def update_from_json(self, json_data):
        PolicyElement.update_from_json(self, json_data)

        if 'algorithm' not in json_data:
            logging.warning('No algorithm defined. Using default.')
            self.algorithm = get_algorithm_by_name()
        else:
            if json_data['algorithm'] in POLICY_ALGORITHMS:
                self.algorithm = get_algorithm_by_name(json_data['algorithm'])
            else:
                raise ValueError(f"Unknown algorithm `{json_data['algorithm']}`.")

        if 'rules' in json_data:
            for rule_data in json_data['rules']:
                self.rules.append(Rule(rule_data))
        else:
            logging.warning("Policy should have at least one rule.")

    def evaluate(self, request):
        if not self.check_target(request):
            return Response(request, decision=RESULT_NOT_APPLICABLE)

        # If we reached this - target is matched with context
        response = None
        for rule in self.rules:
            element_result = rule.evaluate(request)
            # print("Rule (%s) = %s" % (rule, rule_result))
            response, is_final = self.algorithm(response, element_result)
            if is_final:
                # It is final result - skipping the rest
                break

        if request.return_policy_id_list and response.decision != RESULT_NOT_APPLICABLE:
            response.polices.append({
                'element': 'policy',
                'description': self.description,
                'result': response.decision
            })

        return response
# EOF
