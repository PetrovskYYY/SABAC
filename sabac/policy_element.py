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
import logging

__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__version__ = "0.0.0"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"
__status__ = "dev"

# Local source imports
from .action import Obligation, Advice


class PolicyElement:
    """
    Abstract class that includes common elements for rules, policies and policy sets
    """
    def __init__(self, json_data=None, algorithm=None):
        self.description = None
        self.obligations = []
        self.advices = []

        if json_data:
            self.update_from_json(json_data)
        else:
            self.target = None
            # self.obligations = []
            # self.advices = []

        if algorithm:
            self.algorithm = algorithm

    def to_json(self):
        result = {}
        if hasattr(self, 'description') and self.description:
            result['description'] = self.description
        if hasattr(self, 'target') and self.target:
            result['target'] = self.target
        if hasattr(self, 'obligations') and self.obligations:
            result['obligations'] = self.obligations
        if hasattr(self, 'advices') and self.advices:
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
        # else:
        #     logging.warning("Target is a required attribute of policy element.")
            # self.target = None
        if 'obligations' in json_data:
            self.obligations = []
            for obligation in json_data['obligations']:
                self.obligations.append(Obligation(obligation))

        if 'advices' in json_data:
            self.advices = []
            for advice in json_data['advices']:
                self.advices.append(Advice(advice))

    def evaluate(self, context):
        raise NotImplementedError("Unable to evaluate %s." % self.__class__.__name__)

    def check_target(self, request):
        """
        Checks if target is applicable
        :param request:
        :return:
            True - if target matches context
            False - if target NOT matches context
            Exception instance - if exception occurred during check

        """
        if not hasattr(self, 'target') or not self.target:
            # Empty target may be used to group policy elements
            # logging.warning("No target: %s", self)
            return True
        elif not isinstance(self.target, dict):
            raise ValueError("Incorrect target: %s" % self.target)
        return self.context_match(self.target, request)

    @staticmethod
    def context_match(policy_element_requirements, request):
        """
        Compares given criteria with context.
        :param policy_element_requirements: Requirements of current policy element
        :param request: Request object
        :return:
            True - criteria matches with context
            False - criteria NOT matches with context
            Exception instance - if exception occurred during check
        Attributes can be of 3 subtypes: 
        - subject - attributes related to subject that trying to get access
        - resource - attribute related to resource that is to be accessed
        - action - attributes related to action that is to be done
        """
        context = request.attributes
        for policy_key, policy_constraint in policy_element_requirements.items():
            # print("%s - %s" % (key, value))
            if policy_key not in context:
                # Key is NOT in context
                # Requesting attribute value from PDP/PIP
                attribute_value = request.PDP.PIP.get_attribute_value(policy_key, request)
                # Keeping value in request because it could be requested by other policy elements later
                request.attributes[policy_key] = attribute_value

            if isinstance(policy_constraint, dict):
                # We have some advanced comparison
                criteria_value = request.PDP.PIP.evaluate(policy_key, policy_constraint, request)
                if criteria_value is True:
                    continue
                else:
                    return False

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
                return False
        return True

    def __repr__(self):
        return "<{class_name} {data}>".format(
            class_name=self.__class__.__name__,
            data=self.to_json()
        )

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
