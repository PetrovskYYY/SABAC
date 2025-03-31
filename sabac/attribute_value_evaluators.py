#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Functions for evaluation of expressions in rules
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2024, PerinatalCare backend"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"

import logging
import uuid
from typing import Optional, Any

from .request import Request


def calculate_operator_eval(
        policy_information_point,
        attribute_name: str,
        attribute_value: Any,
        operand: Any,
        request: Request
) -> Optional[bool]:
    result = None
    if isinstance(operand, str):
        extracted_attribute_value = policy_information_point.get_attribute_value(operand, request)
        result = attribute_value == extracted_attribute_value
    elif operand is None:
        result = attribute_value is None
    else:  # pragma: no cover
        logging.warning(
            "Only attributes of type string (or None) could be used with operator @ (%s given for %s).",
            operand.__class__.__name__,
            attribute_name
        )
    return result


def equals_operator_eval(
        policy_information_point,
        attribute_name: str,
        attribute_value: Any,
        operand: Any,
        request: Request
) -> Optional[bool]:
    result = None
    if isinstance(operand, str):
        extracted_attribute_value = policy_information_point.get_attribute_value(operand, request)
        result = attribute_value == extracted_attribute_value
    elif operand is None:
        result = attribute_value is None
    else:  # pragma: no cover
        logging.warning(
            "Only attributes of type string (or None) could be used with operator == (%s given for %s).",
            operand.__class__.__name__,
            attribute_name
        )
    return result


def not_equals_operator_eval(
        policy_information_point,
        attribute_name: str,
        attribute_value: Any,
        operand: Any,
        request: Request
) -> Optional[bool]:
    result = None
    if isinstance(operand, str):
        extracted_attribute_value = policy_information_point.get_attribute_value(operand, request)
        result = attribute_value != extracted_attribute_value
    elif operand is None:
        result = attribute_value is not None
    else:  # pragma: no cover
        logging.warning(
            "Only attributes of type string (or None) could be used with operator != (%s given for %s).",
            operand.__class__.__name__,
            attribute_name
        )
    return result


def contains_operator_eval(
        policy_information_point,
        attribute_name: str,
        attribute_value: Any,
        operand: Any,
        request: Request
) -> Optional[bool]:
    if attribute_value is None:
        result = False

    elif not isinstance(attribute_value, list):
        logging.warning(
            "Only attributes of type list could be used with operator @contains (got %s for %s).", attribute_value.__class__.__name__, attribute_name
        )
        result = False

    elif isinstance(operand, list):
        result = any(item in attribute_value for item in operand)

    elif isinstance(operand, dict):
        calculated_attribute_value = policy_information_point.evaluate_attribute_value(operand, request)

        if isinstance(calculated_attribute_value, list):
            result = any(item in attribute_value for item in calculated_attribute_value)
        else:
            result = calculated_attribute_value in attribute_value
    else:
        result = operand in attribute_value
    return result


def contained_in_operator_eval(
        policy_information_point,
        attribute_name: str,
        attribute_value: Any,
        operand: Any,
        request: Request
) -> Optional[bool]:
    result = None
    if isinstance(operand, list):
        if attribute_value in operand:
            return True

        for operand_item in operand:
            if isinstance(operand_item, dict):
                calculated_operand_item_value = policy_information_point.evaluate_attribute_value(operand_item, request)
                if calculated_operand_item_value ==attribute_value:
                    return True

        return False
    elif isinstance(operand, dict):
        calculated_value = policy_information_point.evaluate_attribute_value(operand, request)
        if isinstance(calculated_value, list):
            result = attribute_value in calculated_value
        else:  # pragma: no cover
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


def uuid_operator_eval(
        policy_information_point,
        attribute_name: str,
        attribute_value: Any,
        operand: Any,
        request: Request
) -> Optional[bool]:
    result = None
    if isinstance(operand, str):
        extracted_attribute_value = policy_information_point.get_attribute_value(operand, request)
        result = uuid.UUID(operand)
    else:  # pragma: no cover
        logging.warning(
            "Only attributes of type string could be used with operator @UUID (%s given for %s).",
            operand.__class__.__name__,
            attribute_name
        )
    return result

# "resource.id": {"@not": {"@in": [1]}}
def not_operator_eval(
        policy_information_point,
        attribute_name: str,  # "resource.id"
        attribute_value: Any,  # 3
        operand: Any,  # {"@in": [1]}
        request: Request
) -> Optional[bool]:
    result = None
    if isinstance(operand, dict):
        calculated_operand_value = policy_information_point.evaluate(attribute_name, operand, request)
        result = not calculated_operand_value
        # print(f"{attribute_name}({attribute_value}): not {operand}({calculated_operand_value}) = {result} | {request}")
    else:
        logging.warning(f"Expression '{operand} ({attribute_value})' is invalid.")
    return result


attribute_value_evaluators = {
    '@': calculate_operator_eval,
    '==': equals_operator_eval,
    '!=': not_equals_operator_eval,
    '@contains': contains_operator_eval,
    '@in': contained_in_operator_eval,
    '@UUID': uuid_operator_eval,
    '@not': not_operator_eval,
}
# EOF
