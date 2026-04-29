# Build
REF: https://packaging.python.org/tutorials/packaging-projects/

Install development dependencies first:
```bash
pip install -r requirements-dev.txt
```

Then build:
```shell script
python -m pip install --user --upgrade setuptools wheel
python setup.py sdist bdist_wheel

python -m pip install --user --upgrade twine
python -m twine upload --repository testpypi dist/*
```

# References
- Valid license strings https://autopilot-docs.readthedocs.io/en/latest/license_list.html