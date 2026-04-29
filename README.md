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

# Features
- Full ABAC stack: PDP, PAP, PEP, PIP components
- XACML 3.0 combining algorithms (deny_overrides, permit_overrides, first_applicable, only_one_applicable, ordered variants)
- Async evaluation support for non-ordered algorithms (concurrent policy evaluation via `asyncio.gather()`)
- Type hints throughout core classes
- JSON-based policy definition
- Policy Information Point (PIP) for dynamic attribute resolution

# Installation
```bash
git clone https://github.com/Petrovskiy/SABAC.git
cd SABAC
pip install -r requirements-dev.txt
```

# Quick Start
```python
from sabac import PDP, FilePAP, PIP, DenyBiasedPEP, Request

# Load policies from JSON
pap = FilePAP('policies.json')

# Create Policy Information Point (optional)
pip = PIP()

# Create Policy Decision Point
pdp = PDP(pap_instance=pap, pip_instance=pip)

# Create Policy Enforcement Point
pep = DenyBiasedPEP(pdp)

# Evaluate access
context = {
    'resource.type': 'user',
    'action': 'create',
    'subject.id': 1
}

result = pep.evaluate(context)
print(result)  # True if access granted
```

# Development
See `AGENTS.md` for developer instructions.

# References
1. XACML 3.0 standard http://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html
2. XACML Algorithms combining truth tables https://www.axiomatics.com/blog/understanding-xacml-combining-algorithms/
3. A popular ABAC/XACML introduction in Russian https://habr.com/ru/company/custis/blog/258861/
