#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rule combining algorithms
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"

import logging
from typing import Tuple

from .constants import *

# Rule combining algorithms
# REF: https://www.axiomatics.com/blog/understanding-xacml-combining-algorithms/
from .response import Response


def deny_overrides(old_value, new_value):
    raise NotImplementedError()  # pragma: no cover


def permit_overrides(old_value, new_value):
    raise NotImplementedError()  # pragma: no cover


def deny_unless_permit(old_response, new_response):
    """
    Returns DENY in all cases except explicit permit.
    In case of permit decision considered final
    Combines Old value with new value
    :param old_response: Response of previous evaluation if exists (may be None)
    :param new_response: Response object to combine with te previous response
    :return: Tuple:
        [0] Response object
        [1] Is decision final (True or False)
    """

    if not old_response:
        # There is no previous value to compare
        # First value
        if new_response.decision == RESULT_PERMIT:
            return new_response, True
        else:
            return new_response, False
    elif old_response.decision == RESULT_PERMIT:  # pragma: no cover
        # Strange case - it should not happen
        raise ValueError("deny_unless_permit algorithm with previous permit used again")
    else:
        # Making object copy to avoid source object modification
        result = new_response.copy()

        # Adding advices, obligations and used policies to current response
        result.join_data(old_response, prepend=True)
        if new_response.decision == RESULT_PERMIT:
            return result, True
        elif new_response.decision in [
            RESULT_DENY,
            RESULT_NOT_APPLICABLE,
            RESULT_INDETERMINATE_D,
            RESULT_INDETERMINATE_P,
            RESULT_INDETERMINATE_DP
        ]:
            result.decision = RESULT_DENY
            return result, False
        else:  # pragma: no cover
            raise ValueError('Incorrect result value: %s' % new_response.decision)


def permit_unless_deny(old_response, new_response) -> Tuple[Response, bool]:
    """
    Returns PERMIT in all cases except explicit deny.
    In case of deny decision considered final
    Combines Old value with new value
    :param old_response: Response of previous evaluation if exists (may be None)
    :param new_response: Response object to combine with te previous response
    :return: Tuple:
        [0] Response object
        [1] Is decision final (True or False)
    """
    # Making object copy to avoid source object modification
    result = new_response.copy()

    # Adding advices, obligations and used policies to current response
    result.join_data(old_response, prepend=True)
    if new_response.decision == RESULT_DENY:
        return result, True
    elif new_response.decision in [
        RESULT_PERMIT,
        RESULT_NOT_APPLICABLE,
        RESULT_INDETERMINATE_D,
        RESULT_INDETERMINATE_P,
        RESULT_INDETERMINATE_DP
    ]:
        result.decision = RESULT_PERMIT
        return result, False
    else:  # pragma: no cover
        raise ValueError('Incorrect result value: %s' % new_response.decision)


def first_applicable(old_value, new_value):
    raise NotImplementedError()  # pragma: no cover


def ordered_deny_overrides(old_value, new_value):
    raise NotImplementedError()  # pragma: no cover


def ordered_permit_overrides(old_value, new_value):
    raise NotImplementedError()  # pragma: no cover


# Policy combining algorithms

def only_one_applicable(old_value, new_value):
    raise NotImplementedError()  # pragma: no cover


POLICY_ALGORITHMS = {
    'DENY_OVERRIDES': deny_overrides,
    'PERMIT_OVERRIDES': permit_overrides,
    'DENY_UNLESS_PERMIT': deny_unless_permit,
    'PERMIT_UNLESS_DENY': permit_unless_deny,
    'FIRST_APPLICABLE': first_applicable,
    'ORDERED_DENY_OVERRIDES': ordered_deny_overrides,
    'ORDERED_PERMIT_OVERRIDES': ordered_permit_overrides
}


POLICY_SET_ALGORITHMS = {
    'DENY_OVERRIDES': deny_overrides,  # ['DENY_OVERRIDES', 'Deny-overrides', 'deny_overrides', 'DO']
    'PERMIT_OVERRIDES': permit_overrides,  # ['PERMIT_OVERRIDES', 'Permit-overrides', 'permit_overrides', 'PO']
    'DENY_UNLESS_PERMIT': deny_unless_permit,  # ['Deny-unless-permit','deny-unless-permit','deny_unless_permit', 'DUP']
    'PERMIT_UNLESS_DENY': permit_unless_deny,  # ['Permit-unless-deny', 'permit_unless_deny', 'PUD']
    'FIRST_APPLICABLE': first_applicable,  # ['FIRST_APPLICABLE', 'First-applicable', 'first_applicable', 'FA']
    'ORDERED_DENY_OVERRIDES': ordered_deny_overrides,  # ['ordered_deny_overrides', 'ordered-deny-overrides', 'ODO']
    'ORDERED_PERMIT_OVERRIDES': ordered_permit_overrides,  # 'ordered_permit_overrides','ordered-permit-overrides','OPO'
    'ONLY_ONE_APPLICABLE': only_one_applicable  # 'only-one-applicable', 'only_one_applicable', 'OOA'
}


def get_algorithm_by_name(algorithm_name: str = None, default_algorithm_name=DEFAULT_ALGORITHM_NAME):
    if algorithm_name in POLICY_SET_ALGORITHMS:
        return POLICY_SET_ALGORITHMS[algorithm_name]
    if algorithm_name is not None:
        logging.warning(f"Unknown algorithm name `{algorithm_name}`. "
                        f"Using default algorithm ({default_algorithm_name}) instead.")
    return get_algorithm_by_name(default_algorithm_name)
# EOF
