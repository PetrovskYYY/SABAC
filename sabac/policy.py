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
__license__ = "LGPL"
__email__ = "yuriy.petrovskiy@gmail.com"

import asyncio
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

    def update_algorithm_from_json(self, json_data):
        if 'algorithm' in json_data:
            algorithm = json_data['algorithm']
            if algorithm in POLICY_ALGORITHMS:
                self.algorithm = get_algorithm_by_name(algorithm)
            else:
                raise ValueError(f"Unknown algorithm `{algorithm}`.")
        else:
            logging.warning(f'No algorithm defined. Using default. : {json_data}')
            self.algorithm = get_algorithm_by_name()

    def update_rules_from_json(self, json_data):
        if 'rules' in json_data:
            if isinstance(json_data['rules'], list) and len(json_data['rules']) > 0:
                for rule_data in json_data['rules']:
                    self.rules.append(Rule(rule_data))
            else:
                logging.warning("Policy should have at least one rule.")
        else:
            logging.warning("Policy should have defined rules.")

    def update_from_json(self, json_data):
        PolicyElement.update_from_json(self, json_data)
        self.update_algorithm_from_json(json_data)
        self.update_rules_from_json(json_data)

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

        # If we reached this - the target is matched with context
        response = None
        for rule in self.rules:
            element_result = rule.evaluate(request)
            response, is_final = self.algorithm(old_response=response, new_response=element_result)
            if is_final:
                # It is a final result - skipping the rest
                break

        if request.return_policy_id_list and response.decision != RESULT_NOT_APPLICABLE:
            response.polices.append({
                'element': 'policy',
                'description': self.description,
                'result': response.decision
            })

        return response

    async def evaluate_async(self, request):
        """Async evaluation supporting concurrent rule evaluation for non-ordered algorithms."""
        if not self.check_target(request):
            return Response(request, decision=RESULT_NOT_APPLICABLE)

        # Non-ordered algorithms: evaluate all rules concurrently
        if self.algorithm in [deny_overrides, permit_overrides]:
            tasks = [asyncio.create_task(rule.evaluate_async(request) if hasattr(rule, 'evaluate_async') else asyncio.create_task(asyncio.coroutine(rule.evaluate)(request)))
                      for rule in self.rules]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            # Filter out exceptions
            valid_responses = [r for r in responses if isinstance(r, Response)]
            if not valid_responses:
                return Response(request, decision=RESULT_INDETERMINATE)

            # Call the async version of the algorithm
            if self.algorithm == deny_overrides:
                result, _ = await deny_overrides_async(valid_responses)
            else:
                result, _ = await permit_overrides_async(valid_responses)
            return result
        else:
            # Ordered or other: sequential evaluation with early termination
            response = None
            for rule in self.rules:
                element_result = rule.evaluate(request)
                response, is_final = self.algorithm(old_response=response, new_response=element_result)
                if is_final:
                    break
            return response
# EOF
