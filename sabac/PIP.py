#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Policy Information Point
Responsible for providing information that was not provided in original request.
Information could be gained from:
- environment
- existing request attributes
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, sabac"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__version__ = "0.0.0"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"
__status__ = "dev"

# Standard library imports
import logging
from typing import List, Optional, Any


class InformationProvider:
    """
    Base class for information providers
    """
    def __init__(self):
        self.provided_attributes = None

    @classmethod
    def fetch(cls, request):
        return cls.fetch_value(request.attributes)

    @classmethod
    def fetch_value(cls, request):
        raise NotImplementedError()


class PIP:
    """Policy Information Point"""
    def __init__(self):
        self._information_providers = []
        self._providers_by_provided_attribute = {}

    def evaluate_attribute_value(self, attribute_value: Any, request:"Request") -> Any:
        # FixMe: Avoid calculation requests from userspace
        result = None
        if len(attribute_value) != 1:
            logging.warning(
                'Calculated attributes should have exactly one element, but {element_count} given: {attribute}. '
                'Request: {request}'.format(
                    element_count=len(attribute_value),
                    attribute=attribute_value,
                    request=request
                )
            )
            import traceback
            traceback.print_stack()

        elif '@' in attribute_value:
            logging.debug(f"Evaluating `{attribute_value['@']}`...")
            # Extracting attribute value from context using attribute name
            result = self.get_attribute_value(attribute_value['@'], request)
        else:
            logging.warning("Unknown operator '%s'." % attribute_value)
            raise ValueError("Unknown operator '%s'." % attribute_value)

        return result

    def get_attribute_value(self, attribute_name, request) -> Any:
        attribute_value = self.fetch_attribute(attribute_name, request)

        if isinstance(attribute_value, dict):
            # Attribute value requires evaluation
            evaluated_attribute_value = self.evaluate_attribute_value(attribute_value, request)
            if evaluated_attribute_value is None:
                logging.warning(f"Found no value while evaluating attribute`{attribute_name}` in request {request}.")
            attribute_value = evaluated_attribute_value

        return attribute_value

    def evaluate(self, attribute_name, attribute_value, request) -> bool:
        """
        Evaluates the expression.
        it compares context attribute_value (left side of the expression/dict item key) to the statement
        in the dict value. If dict item value is also a dict more specialized evaluators are used.

        May raise ValueError
        """
        context_attribute_value = self.get_attribute_value(attribute_name, request)
        result = None
        # TODO: Cache value

        if not isinstance(attribute_value, dict):
            # If attribute value is not evaluable we can compare them directly
            result = context_attribute_value == attribute_value

        elif len(attribute_value) != 1:
            raise ValueError('Calculated attributes should have only one element. %d given: %s.' % (
                len(attribute_value),
                attribute_value
            ))

        operation_shortcut = next(iter(attribute_value))

        attribute_value_operations = {
            '@': self.calculate_operator_eval,
            '==': self.equals_operator_eval,
            '!=': self.not_equals_operator_eval,
            '@contains': self.contains_operator_eval,
            '@in': self.contained_in_operator_eval,
        }

        if operation_shortcut in attribute_value_operations:
            result = attribute_value_operations[operation_shortcut](
                attribute_name=attribute_name,
                attribute_value=context_attribute_value,
                operand=attribute_value[operation_shortcut],
                request=request
            )
        else:
            logging.warning("Unknown operator '%s'." % attribute_value.keys())
            raise ValueError("Unknown operator '%s'." % attribute_value.keys())

        return result

    def calculate_operator_eval(
            self,
            attribute_name: str,
            attribute_value: Any,
            operand: Any,
            request: "Request"
    ) -> Optional[bool]:
        result = None
        if isinstance(operand, str):
            extracted_attribute_value = self.get_attribute_value(operand, request)
            result = attribute_value == extracted_attribute_value
        elif operand is None:
            result = attribute_value is None
        else:
            logging.warning(
                "Only attributes of type string (or None) could be used with operator @ (%s given for %s).",
                operand.__class__.__name__,
                attribute_name
            )
        return result

    def equals_operator_eval(
            self,
            attribute_name: str,
            attribute_value: Any,
            operand: Any,
            request: "Request"
    ) -> Optional[bool]:
        result = None
        if isinstance(operand, str):
            extracted_attribute_value = self.get_attribute_value(operand, request)
            result = attribute_value == extracted_attribute_value
        elif operand is None:
            result = attribute_value is None
        else:
            logging.warning(
                "Only attributes of type string (or None) could be used with operator == (%s given for %s).",
                operand.__class__.__name__,
                attribute_name
            )
        return result

    def not_equals_operator_eval(
            self,
            attribute_name: str,
            attribute_value: Any,
            operand: Any,
            request: "Request"
    ) -> Optional[bool]:
        result = None
        if isinstance(operand, str):
            extracted_attribute_value = self.get_attribute_value(operand, request)
            result = attribute_value != extracted_attribute_value
        elif operand is None:
            result = attribute_value is not None
        else:
            logging.warning(
                "Only attributes of type string (or None) could be used with operator != (%s given for %s).",
                operand.__class__.__name__,
                attribute_name
            )
        return result

    def contains_operator_eval(
            self,
            attribute_name: str,
            attribute_value: Any,
            operand: Any,
            request: "Request"
    ) -> Optional[bool]:
        result = None
        if attribute_value is None:
            result = False
        elif not isinstance(attribute_value, list):
            logging.warning(
                "Only attributes of type list could be used with operator @contains (got %s for %s)).",
                attribute_value.__class__.__name__,
                attribute_name
            )
            return False
        elif isinstance(operand, list):
            # If we have a list of values as an argument we check each of them
            for item in operand:
                if item in attribute_value:
                    return True
            # If none matches
            result = False
        elif isinstance(operand, dict):
            # Attribute value should be calculated first
            calculated_attribute_value = self.evaluate_attribute_value(operand, request)

            if isinstance(calculated_attribute_value, list):
                intersection = list(set(calculated_attribute_value) & set(attribute_value))
                result = len(intersection) > 0  # if lists intersect then value is true
            else:
                result = calculated_attribute_value in attribute_value
        else:
            result = operand in attribute_value
        return result

    def contained_in_operator_eval(
            self,
            attribute_name: str,
            attribute_value: Any,
            operand: Any,
            request: "Request"
    ) -> Optional[bool]:
        result = None
        if isinstance(operand, list):
            result = attribute_value in operand
        elif isinstance(operand, dict):
            calculated_value = self.evaluate_attribute_value(operand, request)
            if isinstance(calculated_value, list):
                result = attribute_value in calculated_value
            else:
                logging.warning("Expression '{expression}' value ({calculated_value}) is not a list.".format(
                    expression=operand,
                    calculated_value=calculated_value
                ))
        else:
            logging.warning(
                "Only attribute values of type list (or a expression that is resolving as a list) "
                "could be used with operator @in (%s given for %s).",
                operand.__class__.__name__,
                attribute_name
            )
            result = False
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
        request: "Request",
        attribute_fetch_stack: Optional[List[str]] = None
    ) -> Any:
        """
        Fetches attribute value by given attribute name
        :param attribute_name: Name of an attribute
        :param request: SABAC request object - used for querying sub attributes
        :param attribute_fetch_stack: Stack of attribute names (to prevent the recursion)
        :return: found attribute value of None if attribute not available
        (or error occurred during attribute value resolution)
        """
        # Avoiding search for known attributes
        result = None
        if attribute_name in request.attributes:
            result = request.attributes[attribute_name]
        elif isinstance(attribute_fetch_stack, list):
            if attribute_name in attribute_fetch_stack:
                logging.warning(
                    f"Circular dependency found in attribute call stack "
                    f"while fetching attribute '{attribute_name}': {attribute_fetch_stack}"
                )
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
                    f"No information providers found for attribute '{attribute_name}'. "
                    f"Request data:{request}."
                )
        else:
            for provider in self._providers_by_provided_attribute[attribute_name]:
                # Fetching all required attributes first
                for required_attribute in provider.required_attributes:
                    if required_attribute not in request.attributes:
                        # Searching for required attribute
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


def get_object_by_path(root_object, path_parts, prefix=None):
    """
    Returns object using provided path and root object.
    Functions treats dict keys and class properties as path parts
    :param root_object: dict or class
    :param path_parts: list of strings
    :param prefix: prefix for path (used internally for recursion)
    :return: Value of object that if found by given path or None if path resolution failed.
    """
    sub_object = None
    if isinstance(root_object, dict) and path_parts[0] in root_object:
        # Object is dict
        sub_object = root_object[path_parts[0]]
    elif hasattr(root_object, path_parts[0]):
        # Object is some class that has required attribute or property
        sub_object = getattr(root_object, path_parts[0])
    else:
        full_attribute_name = path_parts[0]
        if prefix is not None:
            full_attribute_name = f"{prefix}.{path_parts[0]}"
        logging.info(
            f"No information providers found for attribute '{full_attribute_name}' "
            f"for object ({root_object.__class__.__name__}){root_object}."
        )
        # logging.warning("root_object '%s'.", root_object)
        # import traceback
        # traceback.print_stack()
        return None

    if len(path_parts) == 1:
        # It is a last portion of given path
        return sub_object

    # There is at least one more level in path
    new_prefix = prefix
    if new_prefix is None:
        new_prefix = path_parts[0]
    else:
        new_prefix = f"{new_prefix}.{path_parts[0]}"

    return get_object_by_path(
        root_object=sub_object,
        path_parts=path_parts[1:],
        prefix=new_prefix
    )
# EOF
