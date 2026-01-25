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
    try:
        result = uuid.UUID(expression)
    except:
        result = None
    return result

expression_evaluators = {
    '@': evaluate_expression,
    '@UUID': uuid_evaluator
}
# EOF
