#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simplified Attribute-Based Access Control
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"

# Rule effect constants
from enum import Enum, auto

EFFECT_PERMIT = 'Permit'
EFFECT_DENY = 'Deny'


# Rule evaluation result constants
class RuleEvaluationResult(Enum):
    PERMIT = auto()
    DENY = auto()
    NOT_APPLICABLE = auto()
    INDETERMINATE = auto()
    INDETERMINATE_D = auto()
    INDETERMINATE_P = auto()
    INDETERMINATE_DP = auto()

    @property
    def shortcut(self):
        if self == self.PERMIT:
            return 'P'
        elif self == self.DENY:
            return 'D'
        elif self == self.NOT_APPLICABLE:
            return 'NA'
        elif self == self.INDETERMINATE:
            return 'I'
        elif self == self.INDETERMINATE_P:
            return 'I/P'
        elif self == self.INDETERMINATE_D:
            return 'I/D'
        elif self == self.INDETERMINATE_DP:
            return 'I/DP'
        else:
            raise ValueError(f"Unexpected rule evaluation result value: {self}")

RESULT_PERMIT = RuleEvaluationResult.PERMIT
RESULT_DENY = RuleEvaluationResult.DENY
RESULT_NOT_APPLICABLE = RuleEvaluationResult.NOT_APPLICABLE
RESULT_INDETERMINATE = RuleEvaluationResult.INDETERMINATE
RESULT_INDETERMINATE_D = RuleEvaluationResult.INDETERMINATE_D
RESULT_INDETERMINATE_P = RuleEvaluationResult.INDETERMINATE_P
RESULT_INDETERMINATE_DP = RuleEvaluationResult.INDETERMINATE_DP

# PEP types
PEP_TYPE_BASE = RESULT_INDETERMINATE
PEP_TYPE_PERMIT_BIASED = EFFECT_PERMIT
PEP_TYPE_DENY_BIASED = EFFECT_DENY

# Shortcuts
PERMIT_SHORTCUTS = ['PERMIT', 'Permit', 'permit', 'P', '+', 1, True]
DENY_SHORTCUTS = ['DENY', 'Deny', 'deny', 'D', '-', 0, False]

UNDETERMINED_RESULTS = [
    RESULT_INDETERMINATE_D,
    RESULT_INDETERMINATE_P,
    RESULT_INDETERMINATE_DP,
    RESULT_NOT_APPLICABLE
]


# Reasons of test failure:
class TestFailReasons(Enum):
    FAILED = auto()
    BAD_FORMAT = auto()
# EOF
