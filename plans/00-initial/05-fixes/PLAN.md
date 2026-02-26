# Implementation Plan

> Source: `.agent/plans/06-testing/PROMPT.md`

## Overview

Fix two bugs in the container startup sequence and add test coverage for the shell scripts that currently have none. The first bug creates a spurious `*` directory in the skills folder due to unguarded bash globs. The second involves the `NANOBOT_NIX_ALLOWED_PACKAGES` variable not behaving as expected, likely due to shell expansion or env-chain issues.

## Architecture & Approach

The project has comprehensive Python test coverage (27 tests across `config_generate.py` and `config_schema.py`) but zero coverage for the three shell scripts (`entrypoint.sh`, `nix-install.sh`, `nix-search.sh`). The shell scripts contain the bugs described in the prompt.

The approach is to:

1. **Fix the `*` directory bug** in `entrypoint.sh` by guarding both glob loops with tightly-scoped `nullglob` (set before the loops, unset after) so they skip when there are no matches.
2. **Extract testable logic** from shell scripts into sourced helper functions. Specifically, extract the skill-symlinking logic from `entrypoint.sh` into `scripts/link-skills.sh`, and extract the whitelist-checking logic from `nix-install.sh` into a sourceable function.
3. **Investigate and fix the allowed-packages bug** in `nix-install.sh` by examining how the `NANOBOT_NIX_ALLOWED_PACKAGES` value (confirmed set to `"*"`) flows through the env chain and how the wildcard/whitelist logic behaves with shell expansion.
4. **Add shell script tests** using `pytest` that source the extracted helper functions and invoke them via `bash -c` calls. This tests the logic directly without requiring the full script flow or nix/nanobot binaries.
5. **Document the Docker user/permissions situation** in CONCERNS.md only — no Dockerfile or docker-compose changes. This is deferred to a future plan.

Shell script tests will follow the same patterns as the existing Python tests: placed in `tests/`, using `pytest`, with fixtures to set up temporary directories and controlled environments. Tests source the helper functions and call them directly via `subprocess` with `bash -c`, making them fast and focused on logic paths (glob handling, whitelist parsing, argument validation) without requiring nix/nanobot runtimes.

## Components

### Entrypoint Glob Fix

**Purpose:** Eliminate the creation of a `*` directory/symlink in the skills directory during container startup.

**Inputs:** The entrypoint script reads from `/opt/nanobot-nix/skills/*/` (built-in skills) and `/mnt/skills/*/` (custom skills).

**Outputs:** Symlinks in `~/.nanobot/workspace/skills/` pointing to skill directories, with no spurious `*` entry.

**Notes:** The fix uses tightly-scoped `nullglob`: set `shopt -s nullglob` before the glob loops and `shopt -u nullglob` immediately after to prevent affecting other parts of the script. This handles both loops cleanly. The skill-symlinking logic will be extracted into `scripts/link-skills.sh` for testability (see Shell Script Test Suite component).

### Nix-Install Whitelist Fix

**Purpose:** Ensure the `NANOBOT_NIX_ALLOWED_PACKAGES` variable correctly controls package installation in all cases.

**Inputs:** `NANOBOT_NIX_ALLOWED_PACKAGES` env var (values: unset, empty string, `*`, comma-separated list).

**Outputs:** Allow/deny decision for a given package name.

**Notes:** The current implementation has these potential edge cases:
- When the value is `*` and the check `!= "*"` is used, this should work correctly if the variable is properly quoted and not shell-expanded
- The `IFS=',' read -ra` parsing may produce unexpected results with trailing commas, empty entries, or whitespace-only entries
- The leading/trailing whitespace trimming uses a bash pattern substitution that may behave differently across bash versions

The whitelist-checking logic should be extracted or at least thoroughly tested in isolation to verify every code path.

### Shell Script Test Suite

**Purpose:** Provide automated test coverage for `entrypoint.sh` and `nix-install.sh` logic.

**Inputs:** Test fixtures providing temporary directories, mock skill directories, and controlled environment variables.

**Outputs:** Pytest test results validating shell script behavior.

**Notes:** The skill-symlinking logic is extracted into `scripts/link-skills.sh` as a standalone helper script. Tests source this helper and invoke its functions via `bash -c` calls in pytest, avoiding the need for nanobot/nix binaries. For `nix-install.sh`, the whitelist-checking logic is extracted into a sourceable function so it can be tested independently without calling `nix profile list` or `nix profile install`. The test framework is pytest+subprocess for now; bats-core may be considered if more shell scripts are added in the future.

### Docker User/Permissions (Investigation Only)

**Purpose:** Document the current root-user situation and identify minimal changes to support local file mounting without permission conflicts.

**Inputs:** `Dockerfile`, `docker-compose.yml`, current volume mount configuration.

**Outputs:** Documented findings and recommendations (no implementation changes unless trivial).

**Notes:** Document only — no implementation changes. The container runs as root because Nix requires root or a configured multi-user setup, the workspace is at `/root/.nanobot/`, and various tools expect root permissions. A full fix would require its own plan. Findings and recommendations are recorded in CONCERNS.md.

## File Manifest

| File | Action | Purpose |
|------|--------|---------|
| `scripts/entrypoint.sh` | Modify | Fix glob handling with scoped nullglob; call extracted link-skills helper |
| `scripts/link-skills.sh` | Create | Extracted skill-symlinking logic from entrypoint for testability |
| `scripts/nix-install.sh` | Modify | Extract whitelist-checking into sourceable function; fix edge cases |
| `tests/test_link_skills.py` | Create | Tests for skill-symlinking logic (sourcing link-skills.sh functions) |
| `tests/test_nix_install.py` | Create | Tests for whitelist validation logic (sourcing nix-install.sh functions) |
