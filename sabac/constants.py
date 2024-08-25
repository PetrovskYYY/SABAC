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

from enum import Enum, auto

DEFAULT_ALGORITHM_NAME = 'DENY_UNLESS_PERMIT'


# Rule effect constants
class RuleEffect(Enum):
    PERMIT = auto()
    DENY = auto()


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
    def shortcut(self) -> str:   # no cover
        if self == self.PERMIT:
            result = 'P'
        elif self == self.DENY:
            result = 'D'
        elif self == self.NOT_APPLICABLE:
            result = 'NA'
        elif self == self.INDETERMINATE:
            result = 'I'
        elif self == self.INDETERMINATE_P:
            result = 'I/P'
        elif self == self.INDETERMINATE_D:
            result = 'I/D'
        elif self == self.INDETERMINATE_DP:
            result = 'I/DP'
        else:
            raise ValueError(f"Unexpected rule evaluation result value: {self}")
        return result


# class PolicyEvaluationResult(RuleEvaluationResult):
# class PolicySetEvaluationResult(PolicySetEvaluationResult):


RESULT_PERMIT = RuleEvaluationResult.PERMIT
RESULT_DENY = RuleEvaluationResult.DENY
RESULT_NOT_APPLICABLE = RuleEvaluationResult.NOT_APPLICABLE
RESULT_INDETERMINATE = RuleEvaluationResult.INDETERMINATE
RESULT_INDETERMINATE_D = RuleEvaluationResult.INDETERMINATE_D
RESULT_INDETERMINATE_P = RuleEvaluationResult.INDETERMINATE_P
RESULT_INDETERMINATE_DP = RuleEvaluationResult.INDETERMINATE_DP


# PEP types
class PolicyEnforcementPointType(Enum):
    BASE = auto()
    PERMIT_BIASED = auto()
    DENY_BIASED = auto()


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

    @property
    def text(self) -> str:  # no cover
        if self == self.FAILED:
            result = 'Test failed'
        elif self == self.BAD_FORMAT:
            result = 'Bad test format'
        else:
            raise ValueError(f"Unexpected test fail reason value: {self}")
        return result
# EOF
