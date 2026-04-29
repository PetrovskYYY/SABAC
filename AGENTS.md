# AGENTS.md

## Commands
- Test: `PYTHONPATH=. pytest` (PYTHONPATH must be set; no `pip install -e .` or requirements.txt)
- Lint: `flake8 . --max-line-length=127`
- Coverage: `PYTHONPATH=. coverage run -m pytest ./tests && coverage report -m`

## Architecture
- Single package: `sabac/` implements ABAC (PDP/PAP/PEP/PIP + policy engine)
- Entrypoint: `sabac/__init__.py` re-exports core classes (PDP, PAP, PEP, PIP, Request, algorithms)
- Tests: `tests/test_sabac.py` with JSON policy fixtures (`test_policies.json`, `policy_tests.json`)

## Notes
- No `requirements.txt`; test deps installed ad-hoc in CI
- Python 3.7+; CI tests 3.7, 3.11, 3.13
- flake8 only; no typechecker or formatter configured
