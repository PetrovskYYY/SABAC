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
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"

import logging
from dataclasses import dataclass
from typing import Optional

from .constants import *
from .policy_element import PolicyElement
from .response import Response
from .request import Request


@dataclass(init=False)
class Rule(PolicyElement):
    effect: RuleEvaluationResult = RuleEvaluationResult.INDETERMINATE
    condition: Optional[dict] = None

    def __init__(self, json_data=None):
        super().__init__(json_data=json_data)

    def to_json(self):
        result = PolicyElement.to_json(self)
        if self.condition is not None:
            result['condition'] = self.condition
        if self.effect is not None:
            result['effect'] = self.effect
        return result

    def update_from_json(self, json_data: dict) -> None:
        PolicyElement.update_from_json(self, json_data)
        if 'effect' in json_data:
            if json_data['effect'] in PERMIT_SHORTCUTS:
                self.effect = RESULT_PERMIT
            elif json_data['effect'] in DENY_SHORTCUTS:
                self.effect = RESULT_DENY
            else:  # pragma: no cover
                raise ValueError('Invalid effect value: %s' % json_data['effect'])
        else:  # pragma: no cover
            raise ValueError(f'No effect in rule: {json_data}')

        if 'condition' in json_data:
            self.condition = json_data['condition']

    def get_conditioned_decision(self, request: Request) -> RuleEvaluationResult:
        result = RuleEvaluationResult.INDETERMINATE
        condition_result = None
        try:
            condition_result = self.context_match(self.condition, request)
        except Exception as e:
            logging.warning(
                f"Exception occurred while evaluating rule {self} in condition evaluation: {str(e)}"
            )

            if self.effect == RuleEffect.PERMIT:
                result = RESULT_INDETERMINATE_P
            elif self.effect == RuleEffect.DENY:
                result = RESULT_INDETERMINATE_D
            else:
                logging.error("Incorrect rule effect value: '%s'", self.effect)
                raise ValueError("Incorrect rule effect value")

            return result

        if not isinstance(condition_result, bool):  # pragma: no cover
            raise ValueError(
                f"Invalid condition evaluation result: ({condition_result.__class__.__name__}){condition_result}"
            )

        if condition_result:
            result = self.effect
        elif condition_result:
            result = RESULT_NOT_APPLICABLE

        return result

    def evaluate(self, request: Request) -> Response:
        response = Response(request, decision=RESULT_NOT_APPLICABLE)

        # Checking target matches request
        if self.check_target(request) is False:
            return response

        if self.condition is not None:
            # Condition is checked after target because it may contain dynamic data on both sides
            # and may be more complex to calculate
            response.decision = self.get_conditioned_decision(request=request)
        else:
            response.decision = self.effect

        # Adding obligations and advices if any defined and match result
        response = self.handle_actions(response)

        # Recording rule to id list if required
        if request.return_policy_id_list is True and response.decision != RESULT_NOT_APPLICABLE:
            response.polices.append({
                'element': 'rule',
                'description': self.description if hasattr(self, 'description') else self,
                'result': response.decision
            })

        return response
# EOF
