#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rule combining algorithms
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__license__ = "LGPL"
__email__ = "yuriy.petrovskiy@gmail.com"

import asyncio
import logging
from typing import Tuple, Optional, List

from .constants import *
from .response import Response


def deny_overrides(old_response: Optional[Response], new_response: Response) -> Tuple[Response, bool]:
    """Non-ordered: Evaluate ALL policies (never early exit)."""
    if old_response is None:
        return new_response, False
    combined = new_response.copy()
    combined.join_data(old_response, prepend=True)
    decisions = [old_response.decision, new_response.decision]
    if RESULT_DENY in decisions:
        combined.decision = RESULT_DENY
    elif RESULT_INDETERMINATE_DP in decisions:
        combined.decision = RESULT_INDETERMINATE_DP
    elif RESULT_INDETERMINATE_D in decisions:
        combined.decision = RESULT_INDETERMINATE_D
    elif RESULT_INDETERMINATE_P in decisions:
        combined.decision = RESULT_INDETERMINATE_P
    elif RESULT_INDETERMINATE in decisions:
        combined.decision = RESULT_INDETERMINATE
    elif RESULT_PERMIT in decisions:
        combined.decision = RESULT_PERMIT
    else:
        combined.decision = RESULT_NOT_APPLICABLE
    return combined, False  # Never final (evaluate all policies)


async def deny_overrides_async(responses: List[Response]) -> Tuple[Response, bool]:
    """Non-ordered async: Evaluate all policies concurrently."""
    if not responses:
        return Response(None, decision=RESULT_NOT_APPLICABLE), True
    combined = responses[0].copy()
    for resp in responses[1:]:
        combined.join_data(resp, prepend=False)
    decisions = [r.decision for r in responses]
    if RESULT_DENY in decisions:
        combined.decision = RESULT_DENY
    elif RESULT_INDETERMINATE_DP in decisions:
        combined.decision = RESULT_INDETERMINATE_DP
    elif RESULT_INDETERMINATE_D in decisions:
        combined.decision = RESULT_INDETERMINATE_D
    elif RESULT_INDETERMINATE_P in decisions:
        combined.decision = RESULT_INDETERMINATE_P
    elif RESULT_INDETERMINATE in decisions:
        combined.decision = RESULT_INDETERMINATE
    elif RESULT_PERMIT in decisions:
        combined.decision = RESULT_PERMIT
    else:
        combined.decision = RESULT_NOT_APPLICABLE
    return combined, True


def permit_overrides(old_response: Optional[Response], new_response: Response) -> Tuple[Response, bool]:
    """Non-ordered: Evaluate ALL policies (never early exit)."""
    if old_response is None:
        return new_response, False
    combined = new_response.copy()
    combined.join_data(old_response, prepend=True)
    decisions = [old_response.decision, new_response.decision]
    if RESULT_PERMIT in decisions:
        combined.decision = RESULT_PERMIT
    elif RESULT_INDETERMINATE_DP in decisions:
        combined.decision = RESULT_INDETERMINATE_DP
    elif RESULT_INDETERMINATE_P in decisions:
        combined.decision = RESULT_INDETERMINATE_P
    elif RESULT_INDETERMINATE_D in decisions:
        combined.decision = RESULT_INDETERMINATE_D
    elif RESULT_INDETERMINATE in decisions:
        combined.decision = RESULT_INDETERMINATE
    elif RESULT_DENY in decisions:
        combined.decision = RESULT_DENY
    else:
        combined.decision = RESULT_NOT_APPLICABLE
    return combined, False  # Never final (evaluate all policies)


async def permit_overrides_async(responses: List[Response]) -> Tuple[Response, bool]:
    """Non-ordered async: Evaluate all policies concurrently."""
    if not responses:
        return Response(None, decision=RESULT_NOT_APPLICABLE), True
    combined = responses[0].copy()
    for resp in responses[1:]:
        combined.join_data(resp, prepend=False)
    decisions = [r.decision for r in responses]
    if RESULT_PERMIT in decisions:
        combined.decision = RESULT_PERMIT
    elif RESULT_INDETERMINATE_DP in decisions:
        combined.decision = RESULT_INDETERMINATE_DP
    elif RESULT_INDETERMINATE_P in decisions:
        combined.decision = RESULT_INDETERMINATE_P
    elif RESULT_INDETERMINATE_D in decisions:
        combined.decision = RESULT_INDETERMINATE_D
    elif RESULT_INDETERMINATE in decisions:
        combined.decision = RESULT_INDETERMINATE
    elif RESULT_DENY in decisions:
        combined.decision = RESULT_DENY
    else:
        combined.decision = RESULT_NOT_APPLICABLE
    return combined, True


def deny_unless_permit(old_response: Optional[Response], new_response: Response) -> Tuple[Response, bool]:
    """
    Returns DENY in all cases except explicit permit.
    In case of permit decision considered final
    Combines Old value with new value
    :param old_response: Response of previous evaluation if exists (maybe None)
    :param new_response: Response object to combine with the previous response
    :return: Tuple:
        [0] Response object
        [1] Is decision final (True or False)
    """
    if not old_response:
        if new_response.decision == RESULT_PERMIT:
            return new_response, True
        else:
            return new_response, False
    elif old_response.decision == RESULT_PERMIT:  # pragma: no cover
        raise ValueError("deny_unless_permit algorithm with previous permit used again")
    else:
        result = new_response.copy()
        result.join_data(old_response, prepend=True)
        if new_response.decision == RESULT_PERMIT:
            return result, True
        elif new_response.decision in [
            RESULT_INDETERMINATE,
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


def permit_unless_deny(old_response: Optional[Response], new_response: Response) -> Tuple[Response, bool]:
    """
    Returns PERMIT in all cases except explicit denying.
    In case of the "deny" decision considered final
    Combines Old value with new value
    :param old_response: Response of previous evaluation if exists (maybe None)
    :param new_response: Response object to combine with the previous response
    :return: Tuple:
        [0] Response object
        [1] Is decision final (True or False)
    """
    result = new_response.copy()
    result.join_data(old_response, prepend=True)
    if new_response.decision == RESULT_DENY:
        return result, True
    elif new_response.decision in [
        RESULT_INDETERMINATE,
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


def first_applicable(old_response: Optional[Response], new_response: Response) -> Tuple[Response, bool]:
    """Return the first non-NOT_APPLICABLE result as final."""
    if new_response.decision != RESULT_NOT_APPLICABLE:
        return new_response, True  # First applicable is final
    return new_response, False


def ordered_deny_overrides(old_response: Optional[Response], new_response: Response) -> Tuple[Response, bool]:
    """Ordered: Stop on first DENY (final)."""
    if old_response and old_response.decision == RESULT_DENY:
        return old_response, True
    if new_response.decision == RESULT_DENY:
        return new_response, True
    if old_response is None:
        return new_response, False
    combined = new_response.copy()
    combined.join_data(old_response, prepend=True)
    decisions = [old_response.decision, new_response.decision]
    if RESULT_DENY in decisions:
        combined.decision = RESULT_DENY
    elif RESULT_INDETERMINATE_DP in decisions:
        combined.decision = RESULT_INDETERMINATE_DP
    elif RESULT_INDETERMINATE_D in decisions:
        combined.decision = RESULT_INDETERMINATE_D
    elif RESULT_INDETERMINATE_P in decisions:
        combined.decision = RESULT_INDETERMINATE_P
    elif RESULT_INDETERMINATE in decisions:
        combined.decision = RESULT_INDETERMINATE
    elif RESULT_PERMIT in decisions:
        combined.decision = RESULT_PERMIT
    else:
        combined.decision = RESULT_NOT_APPLICABLE
    return combined, False


def ordered_permit_overrides(old_response: Optional[Response], new_response: Response) -> Tuple[Response, bool]:
    """Ordered: Stop on first PERMIT (final)."""
    if old_response and old_response.decision == RESULT_PERMIT:
        return old_response, True
    if new_response.decision == RESULT_PERMIT:
        return new_response, True
    if old_response is None:
        return new_response, False
    combined = new_response.copy()
    combined.join_data(old_response, prepend=True)
    decisions = [old_response.decision, new_response.decision]
    if RESULT_PERMIT in decisions:
        combined.decision = RESULT_PERMIT
    elif RESULT_INDETERMINATE_DP in decisions:
        combined.decision = RESULT_INDETERMINATE_DP
    elif RESULT_INDETERMINATE_P in decisions:
        combined.decision = RESULT_INDETERMINATE_P
    elif RESULT_INDETERMINATE_D in decisions:
        combined.decision = RESULT_INDETERMINATE_D
    elif RESULT_INDETERMINATE in decisions:
        combined.decision = RESULT_INDETERMINATE
    elif RESULT_DENY in decisions:
        combined.decision = RESULT_DENY
    else:
        combined.decision = RESULT_NOT_APPLICABLE
    return combined, False


def only_one_applicable(old_response: Optional[Response], new_response: Response) -> Tuple[Response, bool]:
    """Return the applicable policy's decision if exactly one policy is applicable.
    Return INDETERMINATE_DP if >1 applicable (stop early). Return NOT_APPLICABLE if 0 applicable."""
    if old_response is None:
        applicable_count = 0
        applicable_response = None
    else:
        applicable_count = getattr(old_response, 'applicable_count', 0)
        applicable_response = getattr(old_response, 'applicable_response', None)

    if new_response.decision != RESULT_NOT_APPLICABLE:
        applicable_count += 1
        applicable_response = new_response

    if applicable_count > 1:
        result = new_response.copy()
        if old_response:
            result.join_data(old_response, prepend=True)
        result.decision = RESULT_INDETERMINATE_DP
        return result, True  # Early termination

    if old_response:
        result = new_response.copy()
        result.join_data(old_response, prepend=True)
    else:
        result = new_response.copy()

    result.applicable_count = applicable_count
    result.applicable_response = applicable_response

    if applicable_count == 1:
        result.decision = applicable_response.decision
    else:
        result.decision = RESULT_NOT_APPLICABLE

    return result, False


POLICY_ALGORITHMS = {
    'DENY_OVERRIDES': deny_overrides,
    'PERMIT_OVERRIDES': permit_overrides,
    'DENY_UNLESS_PERMIT': deny_unless_permit,
    'PERMIT_UNLESS_DENY': permit_unless_deny,
    'FIRST_APPLICABLE': first_applicable,
    'ORDERED_DENY_OVERRIDES': ordered_deny_overrides,
    'ORDERED_PERMIT_OVERRIDES': ordered_permit_overrides,
    'ONLY_ONE_APPLICABLE': only_one_applicable
}


POLICY_SET_ALGORITHMS = {
    'DENY_OVERRIDES': deny_overrides,
    'PERMIT_OVERRIDES': permit_overrides,
    'DENY_UNLESS_PERMIT': deny_unless_permit,
    'PERMIT_UNLESS_DENY': permit_unless_deny,
    'FIRST_APPLICABLE': first_applicable,
    'ORDERED_DENY_OVERRIDES': ordered_deny_overrides,
    'ORDERED_PERMIT_OVERRIDES': ordered_permit_overrides,
    'ONLY_ONE_APPLICABLE': only_one_applicable
}


def get_algorithm_by_name(algorithm_name: str = None, default_algorithm_name=DEFAULT_ALGORITHM_NAME):
    if algorithm_name in POLICY_SET_ALGORITHMS:
        return POLICY_SET_ALGORITHMS[algorithm_name]
    if algorithm_name is not None:
        logging.warning(f"Unknown algorithm name `{algorithm_name}`. "
                        f"Using default algorithm ({default_algorithm_name}) instead.")
    return get_algorithm_by_name(default_algorithm_name)
# EOF
