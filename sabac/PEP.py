#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Policy Enforcement Point
Usually instance should be located in application core, unlike other classes from this package.
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
# Local source imports
from .constants import *
from .request import Request
from .response import Response


class PEP:
    """
    Policy Enforcement Point
    """
    def __init__(self, pdp_instance, pep_type=PEP_TYPE_DENY_BIASED):
        """

        """
        self.PDP = pdp_instance
        self.type = pep_type

    def get_result(self, context, return_policy_id_list=False, debug=False):
        """
        Returns result object.
        """
        request = Request(attributes=context, return_policy_id_list=return_policy_id_list)
        result = self.PDP.evaluate(request)
        if debug:  # pragma: no cover
            logging.debug("SABAC request: %s, result: %s.", request, result)
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
            elif result.decision in [
                RESULT_INDETERMINATE_D,
                RESULT_INDETERMINATE_P,
                RESULT_INDETERMINATE_DP,
                RESULT_NOT_APPLICABLE
            ]:
                if self.type == PEP_TYPE_BASE:
                    raise ValueError('PDP evaluation result is %s for PEP_TYPE_BASE. This should not occur.' % result)
                elif self.type == PEP_TYPE_DENY_BIASED:
                    return False
                elif self.type == PEP_TYPE_PERMIT_BIASED:
                    return True
                else:
                    raise ValueError('Unexpected PEP type: %s.' % self.type)
        else:
            raise ValueError('Unexpected PDP evaluation result: %s.' % result)

    def evaluate(self, context, return_policy_id_list=False, debug=False):
        """
        Policy Enforcement Point evaluation.
        :param context: Policy context
        :param return_policy_id_list: Should request result contain list of policies that were used
            during making decision
        :param debug: Debug output
        :return:
            True if policy evaluation result is permit,
            False if deny
        """
        result = self.get_result(context, return_policy_id_list, debug)
        return self.evaluate_result(result)


class DenyBiasedPEP(PEP):
    def __init__(self, pdp_instance):
        PEP.__init__(self, pdp_instance=pdp_instance, pep_type=PEP_TYPE_DENY_BIASED)


class PermitBiasedPEP(PEP):
    def __init__(self, pdp_instance):
        PEP.__init__(self, pdp_instance=pdp_instance, pep_type=PEP_TYPE_PERMIT_BIASED)

# EOF
