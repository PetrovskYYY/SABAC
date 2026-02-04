#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Policy Information Point
Responsible for providing information that was not provided in the original request.
Information could be gained from:
- environment
- existing request attributes
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, sabac"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"

import logging
import uuid
from typing import List, Optional, Any

from .expression_evaluators import expression_evaluators
from .operator_evaluators import operator_evaluators
from .information_provider import InformationProvider
from .request import Request
from .utils import get_object_by_path


class PIP:
    """Policy Information Point"""
    def __init__(self):
        self._information_providers = []
        self._providers_by_provided_attribute = {}

    def evaluate_expression(self, expression: Any, request: Request) -> Any:
        if isinstance(expression, dict) and len(expression) == 1:
            # Looks like an expression
            result = None
            key = next(iter(expression))
            if key in expression_evaluators:
                expression_value = expression[key]
                # if isinstance(expression_value, dict) and len(expression) == 1:
                #     expression_value = self.evaluate_expression(expression, request)
                result = expression_evaluators[key](self, expression_value, request)
            else:
                logging.warning(f"Unknown operator '{key}' in expression {expression}.")
            return result
        else:
            # Not an expression - returning as is
            return expression

    # def evaluate_expression(self, attribute_value: Any, request: Request) -> Any:
    #     # FixMe: Avoid calculation requests from userspace
    #     result = None
    #     if len(attribute_value) != 1:
    #         logging.warning(
    #             'Calculated attributes should have exactly one element, but {element_count} given: {attribute}. '
    #             'Request: {request}'.format(
    #                 element_count=len(attribute_value),
    #                 attribute=attribute_value,
    #                 request=request
    #             )
    #         )
    #         import traceback
    #         traceback.print_stack()
    #
    #     elif '@' in attribute_value:
    #         # logging.debug(f"Evaluating `{attribute_value['@']}`...")
    #         # Extracting attribute value from context using attribute name
    #         result = self.get_attribute_value(attribute_value['@'], request)
    #     elif '@UUID' in attribute_value:
    #         # Extracting attribute value from context using the attribute name
    #         try:
    #             result = uuid.UUID(attribute_value['@UUID'])
    #         except:
    #             result = None
    #     else:
    #         result = attribute_value
    #         # logging.warning("Unknown operator '%s'." % attribute_value)
    #         # raise ValueError("Unknown operator '%s'." % attribute_value)
    #
    #     return result

    def get_attribute_value(self, attribute_name, request) -> Any:
        attribute_value = self.fetch_attribute(attribute_name, request)

        # if isinstance(attribute_value, dict):
        #     # Attribute value requires evaluation
        #     evaluated_attribute_value = self.evaluate_expression(attribute_value, request)
        #     if evaluated_attribute_value is None:
        #         logging.warning(f"Found no value while evaluating attribute `{attribute_name}` in request {request}.")
        #     attribute_value = evaluated_attribute_value

        return attribute_value

    def evaluate_statement(self, left_part: str, right_part: Any, request: Request) -> bool:
        """
        Evaluates the equivalence or operation between the left and right parts in the context of a request.

        The method retrieves the value of the left_part from the context using the provided request. It then evaluates
        the equivalence or condition depending on the content or structure of the right_part. The method supports
        direct comparison or operation-based evaluation depending on whether right_part is a dictionary or not.

        Parameters:
            left_part (str): Name of the context attribute or key to retrieve its value.
            right_part (Any): Value or operation to be evaluated against the context attribute value.
            request (Request): The specific request context from which attribute values are retrieved.

        Returns:
            bool: The result of the evaluation, where `True` indicates the conditionally evaluated statement is valid
                  or equivalent; otherwise `False`.

        Raises:
            ValueError: If `right_part` is a dictionary with more than one element or contains an unknown operation
                        shortcut.
        """
        context_attribute_value = self.get_attribute_value(left_part, request)
        # result = None
        # TODO: Cache value

        if not isinstance(right_part, dict):
            # If an attribute value is not evaluable, we can compare them directly
            result = (context_attribute_value == right_part)

        elif len(right_part) != 1:
            raise ValueError('Calculated attributes should have only one element. %d given: %s.' % (
                len(right_part),
                right_part
            ))
        else:
            operation_shortcut = next(iter(right_part))

            if operation_shortcut in operator_evaluators:
                right_part_value = right_part[operation_shortcut]
                result = operator_evaluators[operation_shortcut](
                    policy_information_point=self,
                    attribute_name=left_part,
                    attribute_value=context_attribute_value,
                    operand=right_part[operation_shortcut],
                    request=request
                )
                # logging.debug(f"Evaluated `{left_part}`({context_attribute_value}) {operation_shortcut} `{right_part[operation_shortcut]}`: {result}")
            else:
                logging.warning("Unknown operator '%s'." % right_part.keys())
                raise ValueError("Unknown operator '%s'." % right_part.keys())

        return result

    def add_provider(self, provider: InformationProvider) -> None:
        """
        Adds policy information provider
        :param provider:
        :return:
        """
        if not issubclass(provider, InformationProvider):
            raise ValueError("Only subclass of class InformationProvider could be added to PIP.")
        self._information_providers.append(provider)

        # Adding to reversed index
        for provided_attribute in provider.provided_attributes:
            self._providers_by_provided_attribute.setdefault(provided_attribute, []).append(provider)

    def fetch_attribute(
        self,
        attribute_name: str,
        request: Request,
        attribute_fetch_stack: Optional[List[str]] = None
    ) -> Any:
        """
        Fetches attribute value by a given attribute name

        :param attribute_name:  of an attribute
        :param request: SABAC request object - used for querying sub attributes
        :param attribute_fetch_stack: Stack of attribute names (to prevent the recursion)
        :return: found attribute value of None if the attribute was not available
        (or error occurred during attribute value resolution)
        """
        # Avoiding search for known attributes
        result = None
        if attribute_name in request.attributes:
            result = request.attributes[attribute_name]
        # FixMe: Restore loop checking
        # elif isinstance(attribute_fetch_stack, list):
        #     if attribute_name in attribute_fetch_stack:
        #         logging.warning(
        #             f"Circular dependency found in attribute call stack "
        #             f"while fetching attribute '{attribute_name}': {attribute_fetch_stack}"
        #         )
        # Attribute is absent in context
        elif attribute_name not in self._providers_by_provided_attribute:
            # There is no direct match for this attribute - will try to resolve
            attribute_name_parts = attribute_name.split('.')
            if len(attribute_name_parts) > 1:
                # Attribute is complex - trying to resolve
                result = get_object_by_path(request.attributes, attribute_name_parts)
            else:
                # There is no way to get this attribute
                logging.warning(
                    f"No information providers found for attribute '{attribute_name}'."
                    f" Request data:{request}."
                    f" Attribute fetch stack: {attribute_fetch_stack}"
                )
                import traceback
                traceback.print_stack()
        else:
            for provider in self._providers_by_provided_attribute[attribute_name]:
                # Fetching all required attributes first
                for required_attribute in provider.required_attributes:
                    if required_attribute not in request.attributes:
                        # Searching for the required attribute
                        new_fetch_stack = self._new_attribute_fetch_stack(attribute_name, attribute_fetch_stack)
                        request.attributes[required_attribute] = self.fetch_attribute(
                            required_attribute,
                            request,
                            new_fetch_stack
                        )

                # Now all required attributes should be present in context
                result = provider.fetch(request)
                if result is not None:
                    break
        return result

    @staticmethod
    def _new_attribute_fetch_stack(attribute_name: str, old_stack: Optional[List[str]] = None) -> List[str]:
        result = []
        if isinstance(old_stack, list):
            result += old_stack
        result.append(attribute_name)
        return result
# EOF
