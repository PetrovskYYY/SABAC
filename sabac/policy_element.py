#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base class for Policy, Rule and PolicySet

Object structure:
- target - dict
- description - text
- obligations
- advices
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"

from dataclasses import dataclass, field, InitVar
from typing import Optional, List

from .action import Obligation, Advice


@dataclass(repr=False)
class PolicyElement:
    """
    Abstract class that includes common elements for rules, policies and policy sets
    """
    description: Optional[str] = None
    target: Optional[str] = None
    obligations: List[Obligation] = field(default_factory=list)
    advices: List[Advice] = field(default_factory=list)
    json_data: InitVar[Optional[dict]] = None

    def __post_init__(self, json_data: Optional[dict] = None):
        if json_data is not None:
            self.update_from_json(json_data)

    def __repr__(self):
        return "<{class_name} {data}>".format(
            class_name=self.__class__.__name__,
            data=self.to_json()
        )

    def to_json(self):
        result = {}
        if self.description:
            result['description'] = self.description
        if self.target:
            result['target'] = self.target
        if self.obligations:
            result['obligations'] = self.obligations
        if self.advices:
            result['advices'] = self.advices
        return result

    def update_from_json(self, json_data):
        if 'description' in json_data:
            self.description = json_data['description']
        if 'target' in json_data:
            if isinstance(json_data['target'], dict):
                self.target = json_data['target']
            else:
                ValueError("Target should be a dict")

        def add_list_from_json(field, class_):
            if field in json_data:
                setattr(self, field, [class_(obj) for obj in json_data[field]])

        add_list_from_json('obligations', Obligation)
        add_list_from_json('advices', Advice)

    def evaluate(self, context):
        raise NotImplementedError("Unable to evaluate %s." % self.__class__.__name__)

    def check_target(self, request):
        """
        Checks if the target is applicable
        :param request:
        :return:
            True - if target matches context
            False - if target NOT matches context
            Exception instance - if exception occurred during check
        May raise exceptions:
            ValueError
        """
        if not hasattr(self, 'target') or not self.target:
            # Empty target may be used to group policy elements
            # logging.warning("No target: %s", self)
            return True
        elif not isinstance(self.target, dict):
            raise ValueError("Incorrect target: %s" % self.target)
        return self.context_match(self.target, request)

    @staticmethod
    def context_match(policy_element_requirements, request) -> bool:
        """
        Compares given criteria with context.
        :param policy_element_requirements: Requirements of current policy element
        :param request: Request object
        :return:
            True - criteria matches with context
            False - criteria NOT matches with context
        Attributes can be of 3 subtypes:
        - subject - attributes related to the subject that is trying to get access
        - resource - attribute related to the resource that is to be accessed
        - action - attributes related to action that is to be done
        """
        result = True
        context = request.attributes
        for policy_key, policy_constraint in policy_element_requirements.items():
            if policy_key not in context:
                # Key is NOT in context
                # Requesting attribute value from PDP/PIP
                attribute_value = request.PDP.PIP.get_attribute_value(policy_key, request)
                # Keeping value in a request because it could be requested by other policy elements later
                request.attributes[policy_key] = attribute_value

            if isinstance(policy_constraint, dict):
                # We have some advanced comparison
                criteria_value = request.PDP.PIP.evaluate(policy_key, policy_constraint, request)
                if criteria_value is True:
                    continue
                else:
                    result = False
                    break

            if isinstance(context[policy_key], dict):
                # We have some advanced expression in context
                # Replacing expression with constant value
                context[policy_key] = request.PDP.PIP.get_attribute_value(policy_key, request)

            # Comparison by value
            if context[policy_key] == policy_constraint:
                # Exact match - we continue with comparison
                continue
            else:
                # Key exists, but value is wrong
                result = False
                break
        return result

    def handle_actions(self, response):
        if hasattr(self, 'obligations'):
            for obligation in self.obligations:
                if obligation.fulfill_on == response.decision:
                    response.obligations.append(obligation)
        if hasattr(self, 'advices'):
            for advice in self.advices:
                if advice.fulfill_on == response.decision:
                    response.add_advice(advice)
        return response
# EOF
