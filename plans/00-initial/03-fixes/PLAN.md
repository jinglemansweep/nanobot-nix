# Implementation Plan

> Source: `.agent/plans/04-testing-02/PROMPT.md`

## Overview

Add Zhipu AI (Z.AI/GLM) as a recognized provider in the nanobot-nix config system. This involves adding the provider's env var mappings to the schema, creating a convenience alias, updating the example environment file, and extending existing tests to cover the new entries.

## Architecture & Approach

The config system uses a strict schema-driven approach: `config_schema.py` is the single source of truth for all supported environment variables. The generator (`config_generate.py`) rejects any `NANOBOT_*` env var whose suffix is not in `ENV_MAP`, producing the "Unknown config key" warnings seen in the prompt.

Adding Zhipu follows the exact same pattern as every other provider already in the schema. The provider needs two config fields — `apiKey` and `apiBase` — mapped to `providers.zhipu.apiKey` and `providers.zhipu.apiBase` in the output JSON. A convenience alias (`ZHIPU_API_KEY`) follows the naming convention established by the other providers. No changes to the generator logic are required — it is already schema-agnostic by design.

The provider name `zhipu` is used (not `zai` or `glm`) because it matches the env var naming the user already attempted (`NANOBOT_PROVIDERS_ZHIPU_APIKEY`) and is consistent with how other providers reference the company name rather than the model family.

## Components

### Config Schema Extension

**Purpose:** Register `PROVIDERS_ZHIPU_APIKEY` and `PROVIDERS_ZHIPU_APIBASE` as known env var suffixes, mapping them to the appropriate nested JSON config paths.

**Inputs:** None (pure data addition to `config_schema.py`).

**Outputs:** Two new entries in `ENV_MAP`, one new entry in `ALIASES`.

**Notes:**
- `ENV_MAP` entries follow the established pattern: `"PROVIDERS_ZHIPU_APIKEY": ("providers", "zhipu", "apiKey")` and `"PROVIDERS_ZHIPU_APIBASE": ("providers", "zhipu", "apiBase")`.
- `ALIASES` entry: `"ZHIPU_API_KEY": "NANOBOT_PROVIDERS_ZHIPU_APIKEY"` — follows the `<PROVIDER>_API_KEY` convention used by OpenRouter, Anthropic, OpenAI, DeepSeek, and Groq.
- No changes to `DEFAULTS` or `ARRAY_FIELDS` are needed.

### Environment Example Update

**Purpose:** Document the new Zhipu provider env vars in `.env.example` so users can discover them.

**Inputs:** The new `ENV_MAP` and `ALIASES` entries.

**Outputs:** Two new lines in the Provider API Keys section of `.env.example`.

**Notes:**
- Add `NANOBOT_PROVIDERS_ZHIPU_APIKEY=` with alias comment and `NANOBOT_PROVIDERS_ZHIPU_APIBASE=` in the provider section, positioned alongside the other named providers (before the `CUSTOM` entries).

### Test Coverage

**Purpose:** Ensure the new schema entries are validated by existing structural tests and that the full pipeline correctly processes Zhipu env vars.

**Inputs:** Existing test suite in `tests/test_config_schema.py` and `tests/test_config_generate.py`.

**Outputs:** Passing tests that cover the Zhipu provider.

**Notes:**
- The existing structural tests (`test_env_map_values_are_tuples`, `test_aliases_point_to_valid_canonical_names`, `test_no_duplicate_env_map_paths`) already validate all entries in `ENV_MAP` and `ALIASES` generically — adding the new entries automatically gets them covered.
- A dedicated integration test should verify that setting `NANOBOT_PROVIDERS_ZHIPU_APIKEY` and `NANOBOT_PROVIDERS_ZHIPU_APIBASE` produces the correct nested JSON output, similar to the existing `test_generate_full_pipeline` test for OpenRouter.

### Documentation Update

**Purpose:** Update the README provider reference to include Zhipu.

**Inputs:** README.md provider documentation section.

**Outputs:** Zhipu listed alongside other supported providers.

**Notes:**
- The README has a provider configuration table — add Zhipu with its alias and note the default API base URL (`https://api.z.ai/api/coding/paas/v4`).

## File Manifest

| File | Action | Purpose |
|------|--------|---------|
| `scripts/config_schema.py` | Modify | Add `PROVIDERS_ZHIPU_APIKEY` and `PROVIDERS_ZHIPU_APIBASE` to `ENV_MAP`; add `ZHIPU_API_KEY` to `ALIASES` |
| `.env.example` | Modify | Add `NANOBOT_PROVIDERS_ZHIPU_APIKEY` and `NANOBOT_PROVIDERS_ZHIPU_APIBASE` with alias comment |
| `tests/test_config_generate.py` | Modify | Add integration test for Zhipu provider env var processing |
| `README.md` | Modify | Add Zhipu to provider documentation table |
