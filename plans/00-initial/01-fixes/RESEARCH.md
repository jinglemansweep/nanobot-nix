# Research

> Source: `.agent/plans/02-initial-fixes/PROMPT.md`

## shellcheck (pre-commit hook)

- **URL:** https://github.com/koalaman/shellcheck-precommit
- **Status:** Actively maintained; shellcheck itself is a mature, widely-adopted static analysis tool for shell scripts.
- **Latest Version:** The pre-commit mirror at `https://github.com/shellcheck-py/shellcheck-py` tracks shellcheck releases and is compatible with pre-commit. Current rev is in the v0.10.x range.
- **Compatibility:** Works with the existing pre-commit setup. The project has 3 bash scripts (`entrypoint.sh`, `nix-install.sh`, `nix-search.sh`) that use `#!/usr/bin/env bash` with `set -euo pipefail`, so shellcheck will apply cleanly.
- **Key Findings:**
  - The `shellcheck-py` repo provides a pre-commit hook ID `shellcheck` that wraps the binary.
  - Alternatively, `https://github.com/koalaman/shellcheck-precommit` is the official pre-commit integration.
  - Both approaches work; `shellcheck-py` is more commonly used in pre-commit configs.
- **Concerns:** None. Standard integration.

## pytest

- **URL:** https://docs.pytest.org/
- **Status:** Actively maintained, standard Python testing framework.
- **Compatibility:** The project uses Python 3.11 (per Dockerfile). pytest is fully compatible. The config scripts (`config_schema.py`, `config_generate.py`) are pure Python with only stdlib dependencies (`json`, `os`, `copy`, `logging`, `sys`), making them straightforward to test.
- **Key Findings:**
  - Tests will need to handle `config_generate.py`'s import of `config_schema` (relative import from same directory). A `conftest.py` or `sys.path` manipulation may be needed, or the scripts directory could be made into a package.
  - Functions to test: `read_docker_secrets()`, `resolve_aliases()`, `infer_type()`, `set_nested()`, `generate()` from `config_generate.py`, plus the data structures in `config_schema.py`.
- **Concerns:** The `config_generate.py` script imports `config_schema` without a package prefix (line 9: `from config_schema import ...`). Tests will need to either run from the `scripts/` directory or adjust `sys.path`.
