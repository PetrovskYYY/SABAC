#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Policy Enforcement Point
Usually instance should be located in the application core, unlike other classes from this package.
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"

import logging
from typing import List, Dict

from .constants import *
from .exceptions import TestFailedException
from .request import Request
from .response import Response


class PEP:
    """
    Policy Enforcement Point
    """
    def __init__(self, pdp_instance, pep_type: PolicyEnforcementPointType = PolicyEnforcementPointType.DENY_BIASED):
        self.PDP = pdp_instance
        self.type = pep_type

    def get_result(self, context, return_policy_id_list=False, debug=False):
        """
        Returns result object.
        """
        request = Request(attributes=context, return_policy_id_list=return_policy_id_list)
        result = self.PDP.evaluate(request)
        if debug:  # pragma: no cover
            logging.debug("SABAC request: %s, \nresult: %s.", request, result)
        return result

    def evaluate_result(self, result):
        """
        :return:
            True if policy evaluation result is permit,
            False if deny
        """
        if isinstance(result, Response):
            if result.decision == RESULT_PERMIT:
                return True
            elif result.decision == RESULT_DENY:
                return False
            elif result.decision in UNDETERMINED_RESULTS:
                if self.type == PolicyEnforcementPointType.BASE:  # pragma: no cover
                    raise ValueError('PDP evaluation result is %s for PolicyEnforcementPointType.BASE. This should not occur.' % result)
                elif self.type == PolicyEnforcementPointType.DENY_BIASED:
                    return False
                elif self.type == PolicyEnforcementPointType.PERMIT_BIASED:
                    return True
                else:  # pragma: no cover
                    raise ValueError('Unexpected PEP type: %s.' % self.type)
            else:  # pragma: no cover
                raise ValueError(f'Unexpected PDP evaluation result decision type: {result.decision}.')
        else:  # pragma: no cover
            raise ValueError('Unexpected PDP evaluation result: %s.' % result)

    def evaluate(self, context, return_policy_id_list=False, debug=False):
        """
        Policy Enforcement Point evaluation.
        :param context: Policy context
        :param return_policy_id_list: Should request result contain a list of policies that were used
            during making the decision
        :param debug: Debug output
        :return:
            True if a policy evaluation result is permit,
            False if deny
        """
        result = self.get_result(context, return_policy_id_list, debug)
        return self.evaluate_result(result)

    @staticmethod
    def parse_expected_test_result(test: dict):
        result = True
        if 'result' in test:
            if test['result'] in PERMIT_SHORTCUTS:
                result = True
            elif test['result'] in DENY_SHORTCUTS:
                result = False
            else:
                raise TestFailedException(
                    reason=TestFailReasons.BAD_FORMAT,
                    message="Invalid expected test result format"
                )
        return result

    def run_tests(self, tests:List[Dict]) -> List:
        """
        :return:
        :param tests: List of tests in the following format:
                {
                    "description": "Unauthorized users should be able to access authorization",
                    "context": {
                      "user": null,
                      "action": "login"
                    },
                    "result": "Permit"
                }
        :return List of failed tests
        """
        result = []
        for test in tests:
            expected_result = None
            try:
                expected_result = self.parse_expected_test_result(test)
            except TestFailedException as e:
                result.append({
                    'reason': e.reason,
                    'message': e.message,
                    'test': test
                })
            if 'context' in test:
                permit = self.evaluate(test['context'])
                if permit != expected_result:
                    # Rerunning with debug
                    self.evaluate(
                        context=test['context'],
                        return_policy_id_list=True,
                        debug=True
                    )
                    result.append({
                        'reason': TestFailReasons.FAILED,
                        'message': "Test failed",
                        'test': test
                    })
            else:
                result.append({
                    'reason': TestFailReasons.BAD_FORMAT,
                    'message': "Test has no defined context",
                    'test': test
                })
        return result


class DenyBiasedPEP(PEP):
    def __init__(self, pdp_instance):
        PEP.__init__(self, pdp_instance=pdp_instance, pep_type=PolicyEnforcementPointType.DENY_BIASED)


class PermitBiasedPEP(PEP):
    def __init__(self, pdp_instance):
        PEP.__init__(self, pdp_instance=pdp_instance, pep_type=PolicyEnforcementPointType.PERMIT_BIASED)


class BasePEP(PEP):
    def __init__(self, pdp_instance):
        PEP.__init__(self, pdp_instance=pdp_instance, pep_type=PolicyEnforcementPointType.BASE)
# EOF
