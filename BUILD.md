# Build
REF: https://packaging.python.org/tutorials/packaging-projects/
```shell script
python -m pip install --user --upgrade setuptools wheel
python setup.py sdist bdist_wheel

python -m pip install --user --upgrade twine
python -m twine upload --repository testpypi dist/*
```

# References
- Valid license strings https://autopilot-docs.readthedocs.io/en/latest/license_list.html