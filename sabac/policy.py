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
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"

from dataclasses import dataclass, field
from typing import Optional, List, Callable

from .algorithm import *
from .rule import Rule
from .policy_element import PolicyElement
from .response import Response


@dataclass()
class Policy(PolicyElement):
    algorithm: Optional[Callable] = None
    rules: List[Rule] = field(default_factory=list)

    def update_from_json(self, json_data):
        PolicyElement.update_from_json(self, json_data)

        if 'algorithm' in json_data:
            if json_data['algorithm'] in POLICY_ALGORITHMS:
                self.algorithm = get_algorithm_by_name(json_data['algorithm'])
            else:
                raise ValueError(f"Unknown algorithm `{json_data['algorithm']}`.")
        else:
            logging.warning(f'No algorithm defined. Using default. : {json_data}')
            self.algorithm = get_algorithm_by_name()

        if 'rules' in json_data:
            if isinstance(json_data['rules'], list) and len(json_data['rules']) > 0:
                for rule_data in json_data['rules']:
                    self.rules.append(Rule(rule_data))
            else:
                logging.warning("Policy should have at least one rule.")
        else:
            logging.warning("Policy should have defined rules.")

    def to_json(self):
        result = super().to_json()
        if self.algorithm:
            result['algorithm'] = self.algorithm
        if len(self.rules) > 0:
            rules_data = []
            for rule in self.rules:
                rules_data.append(rule.to_json())
            result['rules'] = rules_data
        return result

    def evaluate(self, request):
        if not self.check_target(request):
            return Response(request, decision=RESULT_NOT_APPLICABLE)

        # If we reached this - target is matched with context
        response = None
        for rule in self.rules:
            element_result = rule.evaluate(request)
            response, is_final = self.algorithm(old_response=response, new_response=element_result)
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
