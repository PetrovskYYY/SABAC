#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ABAC Rule class

Object structure:
- target - dict
- description - text
- obligations
- advices
+ condition
+ effect (Permit/Deny)
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
from .constants import *
from .policy_element import PolicyElement
from .response import Response


class Rule(PolicyElement):
    def __init__(self, json_data=None, algorithm=None):
        self.effect = None  # Allow or deny
        self.condition = None  # dict
        PolicyElement.__init__(self, json_data, algorithm)

    def to_json(self):
        result = PolicyElement.to_json(self)
        if hasattr(self, 'condition') and self.condition:
            result['condition'] = self.condition
        if hasattr(self, 'effect') and self.effect:
            result['effect'] = self.effect

        return result

    def update_from_json(self, json_data):
        PolicyElement.update_from_json(self, json_data)
        if 'effect' in json_data:
            if json_data['effect'] in ['PERMIT', 'P', 1, True]:
                self.effect = RESULT_PERMIT
            elif json_data['effect'] in ['DENY', 'D', 0, False]:
                self.effect = RESULT_DENY
            else:
                raise ValueError('Invalid effect value: %s' % json_data['effect'])
        else:
            raise ValueError('No effect in rule')

        if 'condition' in json_data:
            self.condition = json_data['condition']

    def evaluate(self, request):
        response = Response(request)

        if self.check_target(request) is False:
            return Response(request, decision=RESULT_NOT_APPLICABLE)

        condition_result = None
        if hasattr(self, 'condition') and self.condition is not None:
            # try:
            condition_result = self.context_match(self.condition, request)
            # except Exception as e:
            #     result = e
            #     print("Exception occurred during rule condition evaluation: %s" % str(e))
            #     logging.error("Failed to evaluate rule %s", self)
            #     response.decision = RESULT_NOT_APPLICABLE

        if condition_result is None or condition_result is True:
            response.decision = self.effect
        elif condition_result is False:
            response.decision = RESULT_NOT_APPLICABLE
        elif isinstance(condition_result, Exception):
            if self.effect == EFFECT_PERMIT:
                response.decision = RESULT_INDETERMINATE_P
            elif self.effect == EFFECT_DENY:
                response.decision = RESULT_INDETERMINATE_D
            else:
                logging.error("Incorrect rule effect value: '%s'", self.effect)
                raise ValueError("Incorrect rule effect value")

        # Adding obligations and advices if any defined and match result
        response = self.handle_actions(response)

        if request.return_policy_id_list and response.decision != RESULT_NOT_APPLICABLE:
            response.polices.append({
                'element': 'rule',
                'description': self.description if hasattr(self, 'description') else self,
                'result': response.decision
            })

        return response
# EOF
