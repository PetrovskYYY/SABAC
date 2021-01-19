Simple Attribute Based Access Control

# Description
Python implementation of Attribute Based Access Control (ABAC). Design is based on XACML model, butis not it's strict implementation.

# Features


# Example


# TODO

- Implement all combining algorithms

#References
1. XACML 3.0 standard http://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html
2. XACML Algorithms combining truth tables https://xacml.io
3. Popular ABAC/XACML introduction in Russian https://habr.com/ru/company/custis/blog/258861/#rule

# Build
REF: https://packaging.python.org/tutorials/packaging-projects/
```shell script
python -m pip install --user --upgrade setuptools wheel
python setup.py sdist bdist_wheel
twine upload --repository testpypi dist/*
```
