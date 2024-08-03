#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO Add file description
"""
Policy set class

Object structure:
- target - dict
- description - text
- obligations
- advices
+ algorithm [
    DENY_OVERRIDES|PERMIT_OVERRIDES|
    DENY_UNLESS_PERMIT|PERMIT_UNLESS_DENY|
    FIRST_APPLICABLE|
    ORDERED_DENY_OVERRIDES|ORDERED_PERMIT_OVERRIDES|
    ONLY_ONE_APPLICABLE]
- items (Policies or Policy sets)
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
from typing import Optional, Union

from .constants import RESULT_NOT_APPLICABLE
from .policy import Policy
from .policy_element import PolicyElement
from .algorithm import get_algorithm_by_name, POLICY_SET_ALGORITHMS
from .response import Response


class PolicySet(Policy):
    def __init__(self, *args, **kwargs):
        self.items = []
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_algorithm(json_data: dict):
        if 'algorithm' not in json_data:
            logging.warning('No PolicySet algorithm defined. Using default.')
            return get_algorithm_by_name()
        elif json_data['algorithm'] in POLICY_SET_ALGORITHMS:
            return get_algorithm_by_name(json_data['algorithm'])
        else:
            raise ValueError(f"Unknown algorithm {json_data['algorithm']}.")

    @staticmethod
    def create_policy_item(policy_data) -> Optional[Union[Policy, "PolicySet"]]:
        if 'rules' in policy_data:
            return Policy(policy_data)
        elif 'items' in policy_data:
            return PolicySet(policy_data)
        else:
            logging.warning("Unknown policy set item type: %s", policy_data)
            return None

    def update_from_json(self, json_data):
        # Calling base class method
        PolicyElement.update_from_json(self, json_data)
        self.algorithm = self.get_algorithm(json_data)

        for policy_data in json_data.get('items', []):
            self.items.append(self.create_policy_item(policy_data))

        if len(json_data.get('items', [])) == 0:  # pragma: no cover
            logging.warning("Policy set should have at least one policy.")

    def evaluate(self, request):
        if not self.check_target(request):
            return Response(request, decision=RESULT_NOT_APPLICABLE)

        # If we reached this - target is matched with context
        result = None
        for item in self.items:
            item_result = item.evaluate(request)
            # print("Rule (%s) = %s" % (rule, rule_result))
            result, is_final = self.algorithm(result, item_result)
            if is_final:
                # It is final result - returning result without further processing
                return result
        return result

    @property
    def item_count(self):
        if not hasattr(self, 'items') or not self.items or not isinstance(self.items, list):
            return None
        else:
            return len(self.items)

    def add_item(self, data):
        policy_object = None
        if isinstance(data, dict):
            policy_object = Policy(data)
        elif isinstance(data, (Policy, PolicySet)):
            policy_object = data
        else:  # pragma: no cover
            ValueError('Unknown type (%s) was used as policy.' % data.__class__.__name__)

        if not hasattr(self, 'items') or not isinstance(self.items, list):
            self.items = []

        self.items.append(policy_object)
# EOF
