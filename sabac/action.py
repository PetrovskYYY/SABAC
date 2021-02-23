#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Abstract entity for joining code required for both obligations and advices.
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


class Action:
    def __init__(self, json_data):
        from .constants import RESULT_PERMIT, RESULT_DENY
        
        if not isinstance(json_data, dict):  # pragma: no cover
            raise ValueError("Dict should be provided by json_data attribute.")

        if 'action' in json_data:
            self.action = json_data['action']
        else:  # pragma: no cover
            raise ValueError("'action' attribute should be defined. %s" % json_data)

        condition = None
        if 'fulfill_on' in json_data:
            condition = json_data['fulfill_on']
        elif 'if' in json_data:
            condition = json_data['if']
        else:  # pragma: no cover
            raise ValueError("fulfill_on attribute should be defined.")

        if condition:
            if condition in ['PERMIT', 'Permit', 'permit', 'P', '+']:
                self.fulfill_on = RESULT_PERMIT
            elif condition in ['DENY', 'Deny', 'deny', 'D', '-']:
                self.fulfill_on = RESULT_DENY
            else:  # pragma: no cover
                logging.warning("Action element fulfill_on initialized with incorrect value: '%s'.", condition)
                self.fulfill_on = condition

        if 'attributes' in json_data:
            self.attributes = json_data['attributes']
        else:  # pragma: no cover
            raise ValueError("attributes should be defined.")


class Obligation(Action):
    """
        According to standard http://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html#_Toc325047195
        obligation should be executed if PEP understands and it can and will discharge those obligations
        So if obligation is set and policy evaluation result is matched with required result it is added to result.

    """
    pass


class Advice(Action):
    pass


class ActionInstance:
    def __init__(self):
        self.source = None
        self.attributes = {}

    def execute(self):  # pragma: no cover
        raise NotImplementedError()
# EOF
