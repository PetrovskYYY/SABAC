Simple Attribute Based Access Control

# Description
Python implementation of Attribute Based Access Control (ABAC). 
Design is based on XACML model, but is not its strict implementation.

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

#References
1. XACML 3.0 standard http://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html
2. XACML Algorithms combining truth tables https://xacml.io
3. A popular ABAC/XACML introduction in Russian https://habr.com/ru/company/custis/blog/258861/#rule
