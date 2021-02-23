#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simplified Attribute-Based Access Control
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__version__ = "0.0.0"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"
__status__ = "dev"

# Rule effect constants
EFFECT_PERMIT = 'Permit'
EFFECT_DENY = 'Deny'

# Rule evaluation result constants
RESULT_PERMIT = EFFECT_PERMIT
RESULT_DENY = EFFECT_DENY
RESULT_NOT_APPLICABLE = 'NotApplicable'
RESULT_INDETERMINATE = 'Indeterminate'
RESULT_INDETERMINATE_D = 'Indeterminate/D'
RESULT_INDETERMINATE_P = 'Indeterminate/P'
RESULT_INDETERMINATE_DP = 'Indeterminate/DP'

# PEP types3
PEP_TYPE_BASE = RESULT_INDETERMINATE
PEP_TYPE_PERMIT_BIASED = EFFECT_PERMIT
PEP_TYPE_DENY_BIASED = EFFECT_DENY
# EOF
