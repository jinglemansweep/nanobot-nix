# Agent Rules

## Python Virtual Environment

- Before running any quality checks, tests, or Python tooling, ensure a virtualenv exists and is activated:
  1. If `.venv/` does not exist, create it: `python3 -m venv .venv`
  2. Activate it: `source .venv/bin/activate`
  3. Install the project with dev dependencies: `pip install -e ".[dev]"`
- All subsequent commands (`pre-commit`, `pytest`, etc.) must run inside this activated virtualenv.

## Quality Gates

- Before completing any unit of work, run `pre-commit run --all-files` and fix ALL errors and warnings until it passes cleanly.
- Run `pytest` and resolve ALL test failures before proceeding. No skipped or ignored tests.

## Git

- Do NOT include "Co-Authored-By" or any authorship lines in commit messages.
- If the current branch is `main`, ask the user to confirm a new branch name before making any changes. Branch names must follow the convention: `<type>/<short-description>` (e.g. `feat/config-generator`, `fix/entrypoint-nix-path`, `chore/pre-commit-setup`).

## Documentation

- After completing a large unit of work or before a large commit, run the `/documentation` skill to audit all project documentation for accuracy and completeness.
