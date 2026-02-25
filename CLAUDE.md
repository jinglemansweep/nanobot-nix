# Agent Rules

## Quality Gates

- Before completing any unit of work, run `pre-commit run --all-files` and fix ALL errors and warnings until it passes cleanly.
- If any test suites exist in the project, run ALL tests and resolve ALL failures before proceeding. No skipped or ignored tests.

## Git

- Do NOT include "Co-Authored-By" or any authorship lines in commit messages.
- If the current branch is `main`, ask the user to confirm a new branch name before making any changes. Branch names must follow the convention: `<type>/<short-description>` (e.g. `feat/config-generator`, `fix/entrypoint-nix-path`, `chore/pre-commit-setup`).
