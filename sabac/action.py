#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Abstract entity for joining code required for both obligations and advices.
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"

import logging
from dataclasses import dataclass, field
from typing import Any, Optional, Dict

from .constants import RESULT_PERMIT, RESULT_DENY, PERMIT_SHORTCUTS, DENY_SHORTCUTS, RuleEvaluationResult


@dataclass(init=False)
class Action:
    action: Optional[str] = None
    fulfill_on: Optional[RuleEvaluationResult] = None
    attributes: Optional[Dict[str, Any]] = None

    def __init__(self, json_data):
        if not isinstance(json_data, dict):  # pragma: no cover
            raise ValueError("Dict should be provided by json_data attribute.")

        self.extract_action_from_json(json_data)
        self.extract_condition_from_json(json_data)
        self.extract_attributes_from_json(json_data)

    def extract_action_from_json(self, json_data):
        if 'action' in json_data:
            self.action = json_data['action']
        else:  # pragma: no cover
            raise ValueError("'action' attribute should be defined. %s" % json_data)

    def extract_condition_from_json(self, json_data):
        if 'fulfill_on' in json_data:
            condition = json_data['fulfill_on']
        elif 'if' in json_data:
            condition = json_data['if']
        else:  # pragma: no cover
            raise ValueError("fulfill_on attribute should be defined for any obligation or advice.")

        if condition:
            if condition in PERMIT_SHORTCUTS:
                self.fulfill_on = RESULT_PERMIT
            elif condition in DENY_SHORTCUTS:
                self.fulfill_on = RESULT_DENY
            else:  # pragma: no cover
                logging.warning("Action element fulfill_on initialized with incorrect value: '%s'.", condition)
                self.fulfill_on = condition

    def extract_attributes_from_json(self, json_data):
        if 'attributes' in json_data:
            self.attributes = json_data['attributes']
        else:  # pragma: no cover
            raise ValueError("attributes should be defined.")


class Obligation(Action):
    """
        According to standard, https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html#_Toc325047195
        obligation should be executed if PEP understands, and it can and will discharge those obligations
        So if obligation is set and a policy evaluation result is matched with a required result, it is added to the result.
    """
    pass


class Advice(Action):
    pass


@dataclass()
class ActionInstance:
    source: Any = None
    attributes: Dict = field(default_factory={})

    def execute(self):
        raise NotImplementedError()  # pragma: no cover

# EOF
