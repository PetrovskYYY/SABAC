#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Expression evaluators
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2026, Rating backend"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = ""  # TODO Add licence
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"

import uuid
from typing import Any

# from sabac import Request


def evaluate_expression(policy_information_provider: "PIP", expression: Any, request: 'Request') -> Any:
    return policy_information_provider.get_attribute_value(expression, request)


def uuid_evaluator(policy_information_provider: "PIP", expression: Any, request: 'Request') -> Any:
    expression_value = expression
    if isinstance(expression, dict) and len(expression) == 1:
        expression_value = policy_information_provider.evaluate_expression(expression, request)
    try:
        if isinstance(expression_value, list):
            result = []
            for item in expression_value:
                result.append(uuid.UUID(item))
        else:
            result = uuid.UUID(expression_value)
    except:
        result = None

    # print(f"UUID: ({expression.__class__.__name__}){expression} => {expression_value} = {result}")
    return result


def str_evaluator(policy_information_provider: "PIP", expression: Any, request: 'Request') -> Any:
    try:
        result = str(expression)
    except:
        result = None
    return result


expression_evaluators = {
    '@': evaluate_expression,
    '@UUID': uuid_evaluator,
    '@STR': str_evaluator
}
# EOF
