# Implementation Plan

> Source: `.agent/plans/02-initial-fixes/PROMPT.md`

## Overview

This plan delivers four improvements to the nanobot-nix project: adding local build support to `docker-compose.yml`, creating a pytest test suite for the config Python scripts (with supporting project structure: `pyproject.toml`, package conversion, and CI workflow), integrating shellcheck into pre-commit, and adding a new Claude Code "documentation" skill with corresponding CLAUDE.md updates.

## Architecture & Approach

All four items are independent and touch distinct parts of the codebase with no ordering dependencies between them. The approach is conservative — each change integrates with existing patterns (pre-commit config format, docker-compose structure, Claude skill conventions) rather than introducing new tooling or abstractions.

For Docker Compose, the standard approach is to add `build:` alongside `image:` using YAML anchors or a common profile, so `docker compose build` and `docker compose up --build` work while the default `docker compose up` still pulls the pre-built image.

For pytest, tests will live in a `tests/` directory at the project root. The `scripts/` directory will be converted into a proper Python package (with `__init__.py`) so it can be imported directly. A `pyproject.toml` at the project root will define the package and dev dependencies. Tests will cover all public functions in `config_generate.py` and validate the data structures in `config_schema.py`.

For shellcheck, the `shellcheck-py` pre-commit hook will be added to `.pre-commit-config.yaml` targeting the three existing shell scripts.

For the documentation skill, a new `.claude/skills/documentation/SKILL.md` file will define a skill that systematically reviews all documentation against the actual codebase state. CLAUDE.md will be updated to instruct agents to invoke this skill at appropriate checkpoints.

## Components

### Docker Compose Local Build Support

**Purpose:** Allow users to build the image locally from source instead of always pulling from GHCR.

**Inputs:** The existing `Dockerfile` and `docker-compose.yml`.

**Outputs:** An updated `docker-compose.yml` where both services reference a shared `build:` configuration, enabling `docker compose build` and `docker compose up --build` to work out of the box. The `image:` key is retained so `docker compose pull` and default `up` continue to use the GHCR image.

**Notes:** Docker Compose resolves `build:` and `image:` together — when both are present, `build` is used for local builds and `image` sets the tag name. A YAML anchor (`x-common-build`) avoids duplicating the build config between the two services. The `build:` block should pass through the `NANOBOT_REPO` and `NANOBOT_REF` build args, defaulting to the same values as the Dockerfile.

### Pytest Test Suite for Config Scripts

**Purpose:** Ensure the config generation logic (`config_generate.py` and `config_schema.py`) is correct and remains correct as the schema evolves.

**Inputs:** The Python scripts in `scripts/` (as a proper Python package) and pytest as a test runner.

**Outputs:** A `tests/` directory containing test modules covering:
- `config_schema.py`: Structural validation of `ENV_MAP`, `DEFAULTS`, `ARRAY_FIELDS`, and `ALIASES` (e.g., all ENV_MAP values are tuples, all ARRAY_FIELDS entries exist in ENV_MAP, all ALIASES point to valid canonical names).
- `config_generate.py`: Unit tests for `infer_type()`, `set_nested()`, `resolve_aliases()`, `read_docker_secrets()`, and the full `generate()` pipeline using mocked environment variables and filesystem.

**Notes:**
- The `scripts/` directory will be converted into a Python package by adding `__init__.py`. Internal imports will use relative form (e.g., `from .config_schema import ...`).
- The Dockerfile entrypoint must be updated from `python3 /opt/nanobot-nix/scripts/config_generate.py` to `python3 -m scripts.config_generate`, with the working directory set appropriately or `PYTHONPATH` configured.
- Tests import directly: `from scripts.config_schema import ...` and `from scripts.config_generate import ...`.
- Tests should use `monkeypatch` for environment variable manipulation and `tmp_path` for filesystem operations (Docker secrets dir, output config file).
- The `generate()` function writes to `~/.nanobot/config.json` — tests must patch `os.path.expanduser` or `HOME` to use a temp directory.
- CLAUDE.md quality gate instructions must be updated to include `pytest` as a required test command.

### Python Project Structure (pyproject.toml)

**Purpose:** Formalize the project as an installable Python package with declared dev dependencies.

**Inputs:** The existing `scripts/` package and pytest dependency.

**Outputs:** A `pyproject.toml` at the project root defining:
- The project metadata (name, version, python requirement).
- A `[project.optional-dependencies]` dev section listing `pytest`.
- Package discovery configuration pointing to `scripts/`.

**Notes:** Contributors can run `pip install -e ".[dev]"` to get a working dev environment. The CI workflow will use this to install dependencies.

### CI Test Workflow

**Purpose:** Gate PRs with automated testing — run pytest and pre-commit checks on every pull request.

**Inputs:** The pytest test suite, pre-commit config, and pyproject.toml.

**Outputs:** A GitHub Actions workflow file (`.github/workflows/test.yml`) that runs on PRs and pushes, executing `pre-commit run --all-files` and `pytest`.

**Notes:** This is a lightweight workflow separate from the existing `build.yml` (which handles Docker image builds). It only needs a Python environment, not Docker.

### Shellcheck Pre-commit Integration

**Purpose:** Enforce shell script quality standards across all `.sh` files in the repository.

**Inputs:** The existing `.pre-commit-config.yaml` and the three shell scripts in `scripts/`.

**Outputs:** An updated `.pre-commit-config.yaml` with a `shellcheck-py` hook entry.

**Notes:** The three existing scripts (`entrypoint.sh`, `nix-install.sh`, `nix-search.sh`) all use bash with `set -euo pipefail`. All shellcheck warnings must be fixed — no `# shellcheck disable=` suppressions. The scripts are small enough that all flagged patterns can be rewritten cleanly.

### Documentation Skill

**Purpose:** Provide a Claude Code skill that systematically audits all project documentation for accuracy, completeness, and consistency with the actual codebase.

**Inputs:** The entire repository contents, specifically: `README.md`, `CLAUDE.md`, `.env.example`, docstrings in Python files, inline comments in shell scripts, and `skills/toolbox/SKILL.md`.

**Outputs:** A `.claude/skills/documentation/SKILL.md` file defining the skill's behavior. The skill should:
1. Inventory all documentation files and significant inline documentation.
2. Cross-reference documented features, variables, paths, and behaviors against the actual code.
3. Identify stale, missing, or inaccurate documentation.
4. Produce a report of findings and apply fixes.

**Notes:**
- The skill should check that environment variable tables in README.md match `config_schema.py`'s `ENV_MAP` and `ALIASES`.
- It should verify that file paths, commands, and build arguments mentioned in documentation actually exist.
- It should check that CLAUDE.md agent rules reflect the current project structure and tooling.
- CLAUDE.md must be updated to instruct agents to invoke this skill after large units of work or before large commits.

## File Manifest

| File | Action | Purpose |
|------|--------|---------|
| `docker-compose.yml` | Modify | Add `build:` configuration alongside existing `image:` for local build support |
| `.pre-commit-config.yaml` | Modify | Add shellcheck-py hook |
| `CLAUDE.md` | Modify | Add pytest to quality gate instructions; add documentation skill invocation rule |
| `scripts/__init__.py` | Create | Make scripts/ a proper Python package |
| `scripts/config_generate.py` | Modify | Change `from config_schema import ...` to relative import `from .config_schema import ...` |
| `Dockerfile` | Modify | Add `WORKDIR /opt/nanobot-nix` so `python -m scripts.config_generate` resolves correctly |
| `scripts/entrypoint.sh` | Modify | Fix shellcheck warnings; update Python invocation to `python3 -m scripts.config_generate` |
| `scripts/nix-install.sh` | Modify | Fix all shellcheck warnings |
| `scripts/nix-search.sh` | Modify | Fix all shellcheck warnings |
| `pyproject.toml` | Create | Project metadata, package config, dev dependencies (pytest) |
| `tests/test_config_schema.py` | Create | Tests for config_schema.py data structures |
| `tests/test_config_generate.py` | Create | Tests for config_generate.py functions |
| `.github/workflows/test.yml` | Create | CI workflow running pytest and pre-commit on PRs |
| `.claude/skills/documentation/SKILL.md` | Create | Documentation audit skill definition |
