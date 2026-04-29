# AGENTS.md

## Commands
- Install deps: `pip install -r requirements-dev.txt`
- Test: `PYTHONPATH=. pytest` (PYTHONPATH must be set; no `pip install -e .`)
- Lint: `flake8 . --max-line-length=127`
- Coverage: `PYTHONPATH=. coverage run -m pytest ./tests && coverage report -m`

## Architecture
- Single package: `sabac/` implements ABAC (PDP/PAP/PEP/PIP + policy engine)
- Entrypoint: `sabac/__init__.py` re-exports core classes (PDP, PAP, PEP, PIP, Request, algorithms)
- Tests: `tests/test_sabac.py` with JSON policy fixtures (`test_policies.json`, `policy_tests.json`, `test_policies_algorithms.json`)
- Async support: Non-ordered algorithms (`deny_overrides`, `permit_overrides`) support async concurrent evaluation via `asyncio.gather()`

## Test Dependencies
- pytest
- pytest-asyncio (for async tests)

## Notes
- `requirements-dev.txt` contains development dependencies
- Python 3.7+; CI tests 3.7, 3.11, 3.13
- flake8 only; no typechecker or formatter configured
- Async methods (`evaluate_async`) available for `Policy` and `PolicySet` classes
