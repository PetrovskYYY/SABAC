#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO Add file description
"""

"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2021, Exam backend"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__version__ = "0.0.0"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"
__status__ = "dev"

# Local source imports
from sabac import PDP, PAP, DenyBiasedPEP, deny_unless_permit

# Creating Policy Administration Point
pap = PAP(deny_unless_permit)

# Adding policy to PAP
pap.add_item({
    "description": "Admin permissions",
    "target": {
        'subject.id': 1,
    },
    "algorithm": "DENY_UNLESS_PERMIT",
    'rules': [
        {
            "effect": "PERMIT",
            "description": "Allow to manage users",
            "target": {
                'resource.type': 'user',
                'action': {'@in': ['create', 'view', 'update', 'erase_personal_data', 'delete']},
            },
        }
    ]
})

pdp = PDP(pap_instance=pap)

# Creating Policy Enforcement Point
pep = DenyBiasedPEP(pdp)

# Describing Policy Enforcement Point context
context = {
    'resource.type': 'user',
    'action': 'create',
    'subject.id': 1
}

# Evaluating policy
result = pep.evaluate(context)

print(result)  # Should return True

# EOF
