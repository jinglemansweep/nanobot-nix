# Research

> Source: `.agent/plans/06-testing/PROMPT.md`

No external references found in the prompt. Both issues reference internal project components (entrypoint shell scripts, environment variables, Docker configuration).

## Internal Investigation

### Bug 1: "*" directory in skills

**Root cause identified in `scripts/entrypoint.sh` lines 22-30.**

The entrypoint uses `for dir in .../*/;` loops to symlink skills. In bash, when a glob pattern has no matches and `nullglob` is not set (the default), the literal glob string is preserved. This means:

- If `/opt/nanobot-nix/skills/` has no subdirectories → the loop iterates once with the literal `/opt/nanobot-nix/skills/*/` → `basename` returns `*` → creates a symlink named `*`
- If `/mnt/skills/` exists but has no subdirectories → same result

In the standard docker-compose setup with the volume mount `./skills:/mnt/skills:ro`, this shouldn't happen because `toolbox/` exists. However, it would occur when:
1. The container is run standalone without a `/mnt/skills` mount but an empty `/mnt/skills` directory exists
2. The build-time `COPY skills/` copies an empty directory
3. A user mounts an empty skills directory

### Bug 2: Allowed packages variable

**`NANOBOT_NIX_ALLOWED_PACKAGES` handling spans two files:**

- `scripts/config_generate.py` — correctly ignores it via `IGNORED_ENV_VARS`
- `scripts/nix-install.sh` — uses it for whitelist validation

The `nix-install.sh` logic appears correct when read in isolation, but there are no automated tests for the shell scripts. The bug may involve:
- The env var not surviving the Docker env chain (`.env` → docker-compose → container)
- The `*` wildcard value being shell-expanded in certain contexts
- The `IFS=',' read -ra` parsing having edge cases with whitespace or empty entries

### Test coverage gaps

- **Shell scripts have zero test coverage** — `entrypoint.sh`, `nix-install.sh`, and `nix-search.sh` are untested
- **Python tests cover only `config_generate.py` and `config_schema.py`** (27 tests)
- No integration tests for the full startup sequence
