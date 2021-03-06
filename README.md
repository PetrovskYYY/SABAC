=====================================
Simple Attribute Based Access Control
=====================================
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![travis status](https://travis-ci.org/PetrovskYYY/SABAC.svg?branch=master)](https://travis-ci.org/PetrovskYYY/SABAC)
[![Documentation Status](https://readthedocs.org/projects/sabac/badge/?version=latest)](https://sabac.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/sabac.svg)](http://badge.fury.io/py/sabac)
[![Coverage Status](https://coveralls.io/repos/github/PetrovskYYY/SABAC/badge.svg?branch=master)](https://coveralls.io/github/PetrovskYYY/SABAC?branch=master)
[![Code Climate](https://codeclimate.com/github/PetrovskYYY/SABAC/badges/gpa.svg)](https://codeclimate.com/github/PetrovskYYY/SABAC)

# Description
Python implementation of Attribute Based Access Control (ABAC). 
Design is based on XACML model, but is not its strict implementation.

# Install
```
pip install sabac
```

# Features


# Example
```python
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
```

# TODO

- Implement all combining algorithms

# References
1. XACML 3.0 standard http://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html
2. XACML Algorithms combining truth tables https://www.axiomatics.com/blog/understanding-xacml-combining-algorithms/
3. A popular ABAC/XACML introduction in Russian https://habr.com/ru/company/custis/blog/258861/#rule
