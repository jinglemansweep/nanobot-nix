# Implementation Plan — Remove Config Mapping Layer

> Source: `plans/01-config-expansion/00-initial/PROMPT.md`

## Overview

Remove the custom config mapping layer (`scripts/config_schema.py` + `scripts/config_generate.py`) entirely. Nanobot already supports native Pydantic env var configuration via `BaseSettings` with `env_prefix="NANOBOT_"` and `env_nested_delimiter="__"`. Every config field is already available as an env var (e.g., `NANOBOT_CHANNELS__TELEGRAM__TOKEN`). Our custom mapping layer is redundant.

The entrypoint will be simplified to replace the Python config generator with a shell-based Docker secrets export loop. All other config is handled natively by Pydantic.

## Architecture & Approach

Nanobot's upstream `BaseSettings` configuration means:

- **Naming convention:** `NANOBOT_` prefix + `__` as nested delimiter + snake_case field names. Example: `NANOBOT_CHANNELS__TELEGRAM__TOKEN`, `NANOBOT_PROVIDERS__ANTHROPIC__API_KEY`.
- **Type handling:** Pydantic handles bool, int, float natively from string env vars. Lists and dicts require JSON syntax (e.g., `["user1","user2"]`).
- **No aliases needed:** Users set the canonical Pydantic env var directly.
- **No defaults override needed:** Upstream defaults apply natively.
- **No config.json generation needed:** Pydantic reads env vars directly at runtime.

The only entrypoint responsibility that remains is Docker secrets injection — reading files from `/run/secrets/NANOBOT_*` and exporting them as env vars so Pydantic can pick them up.

## Components

### Files to Delete

| File | Reason |
|------|--------|
| `scripts/config_schema.py` | Custom ENV_MAP, DEFAULTS, ARRAY_FIELDS, ALIASES — all redundant with Pydantic native env vars |
| `scripts/config_generate.py` | Custom config generation pipeline — no longer needed |
| `scripts/__init__.py` | Python package init — no Python modules remain in scripts/ |
| `tests/test_config_schema.py` | Tests for deleted schema module |
| `tests/test_config_generate.py` | Tests for deleted generator module |

### Modified: `scripts/entrypoint.sh`

**Change:** Replace `python3 -m scripts.config_generate` (line 16) with a shell-based Docker secrets export loop.

**New Step 3:**

```bash
# Step 3: Docker secrets → env vars
if [ -d /run/secrets ]; then
  for secret in /run/secrets/NANOBOT_*; do
    [ -f "$secret" ] || continue
    name="$(basename "$secret")"
    if [ -z "${!name:-}" ]; then
      export "$name"="$(cat "$secret" | tr -d '\n')"
    fi
  done
fi
```

This preserves the existing behaviour where env vars take precedence over secrets (the `if [ -z "${!name:-}" ]` check skips secrets when the env var is already set).

No default model override is needed — upstream defaults apply natively.

### Modified: `.env.example`

**Change:** Rewrite to document native Pydantic env var format.

**Key changes:**
- All env vars use `NANOBOT_` prefix with `__` nested delimiter (e.g., `NANOBOT_PROVIDERS__ANTHROPIC__API_KEY`)
- Remove alias references (no mapping layer to provide aliases)
- Note that list values require JSON array syntax (e.g., `["user1","user2"]`)
- Keep the `NANOBOT_NIX_ALLOWED_PACKAGES` section unchanged (consumed by `nix-install.sh`, not Pydantic — safe because Pydantic ignores unknown fields without a matching `__`-delimited schema path)
- Add sections for commonly used fields from all channels and providers

### Modified: `README.md`

**Change:** Rewrite Configuration Reference section (lines 31-99).

**Key changes:**
- Explain Pydantic native env vars (prefix + delimiter convention)
- Remove all alias columns/references
- Update env var names to `__` delimiter format throughout
- Update Docker secrets section to reference new `__`-delimited secret file names
- Document JSON array syntax for list fields (replaces CSV)
- Update example env var names in all sections

### Modified: `pyproject.toml`

**Change:** Remove `include = ["scripts*"]` from `[tool.setuptools.packages.find]` since no Python packages remain in `scripts/` after deletion. Keep `[project.optional-dependencies] dev = ["pytest"]` since `test_link_skills.py` and `test_nix_install.py` remain.

### Dropped from Original Plan

- **config-schema-sync skill** (`.claude/skills/config-schema-sync/SKILL.md`) — no mapping layer to sync against. Users configure Pydantic env vars directly from upstream docs.

## File Manifest

| File | Action | Purpose |
|------|--------|---------|
| `scripts/config_schema.py` | Delete | Remove redundant custom schema mapping |
| `scripts/config_generate.py` | Delete | Remove redundant config generator |
| `scripts/__init__.py` | Delete | Remove empty Python package init |
| `tests/test_config_schema.py` | Delete | Remove tests for deleted schema |
| `tests/test_config_generate.py` | Delete | Remove tests for deleted generator |
| `scripts/entrypoint.sh` | Modify | Replace Python config generator call with shell-based Docker secrets export |
| `.env.example` | Modify | Rewrite for native Pydantic env var format |
| `README.md` | Modify | Update Configuration Reference for native env vars |
| `pyproject.toml` | Modify | Remove `scripts*` from setuptools package find |

## Implementation Order

1. Delete the five files (schema, generator, init, and their tests)
2. Update `scripts/entrypoint.sh` with Docker secrets loop
3. Update `pyproject.toml` to remove scripts package
4. Rewrite `.env.example` with native Pydantic env var format
5. Rewrite `README.md` Configuration Reference section
6. Run remaining tests (`test_link_skills.py`, `test_nix_install.py`) to verify no breakage
7. Run `pre-commit run --all-files` to verify quality gates
