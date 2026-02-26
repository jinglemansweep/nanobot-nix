# Task List

> Source: `.agent/plans/04-testing-02/PLAN.md`

## Config Schema Extension

- [x] **Add Zhipu `ENV_MAP` entries to `scripts/config_schema.py`** — In `scripts/config_schema.py`, add two new entries to the `ENV_MAP` dict, positioned after the `PROVIDERS_GROQ_APIKEY` entry and before the `PROVIDERS_CUSTOM_APIKEY` entry:
  - `"PROVIDERS_ZHIPU_APIKEY": ("providers", "zhipu", "apiKey")`
  - `"PROVIDERS_ZHIPU_APIBASE": ("providers", "zhipu", "apiBase")`
  - Verify: run `python -c "from scripts.config_schema import ENV_MAP; assert 'PROVIDERS_ZHIPU_APIKEY' in ENV_MAP; assert 'PROVIDERS_ZHIPU_APIBASE' in ENV_MAP; print('OK')"`.

- [ ] **Add Zhipu `ALIASES` entry to `scripts/config_schema.py`** — In `scripts/config_schema.py`, add one new entry to the `ALIASES` dict, positioned after the `GROQ_API_KEY` entry:
  - `"ZHIPU_API_KEY": "NANOBOT_PROVIDERS_ZHIPU_APIKEY"`
  - Verify: run `python -c "from scripts.config_schema import ALIASES; assert ALIASES['ZHIPU_API_KEY'] == 'NANOBOT_PROVIDERS_ZHIPU_APIKEY'; print('OK')"`.

## Environment Example Update

- [ ] **Add Zhipu env vars to `.env.example`** — In `.env.example`, add two new lines in the "Provider API Keys" section, after the `NANOBOT_PROVIDERS_GROQ_APIKEY=` line and before the `NANOBOT_PROVIDERS_CUSTOM_APIKEY=` line:
  - `NANOBOT_PROVIDERS_ZHIPU_APIKEY=           # Alias: ZHIPU_API_KEY`
  - `NANOBOT_PROVIDERS_ZHIPU_APIBASE=`
  - Maintain the same alignment as the existing alias comments (column-align the `#` with the other alias comments above).

## Test Coverage

- [ ] **Verify existing structural tests pass with new schema entries** — Run `pytest tests/test_config_schema.py -v` and confirm all tests pass. The existing generic tests (`test_env_map_values_are_tuples`, `test_env_map_values_contain_strings`, `test_aliases_point_to_valid_canonical_names`, `test_no_duplicate_env_map_paths`) automatically cover the new Zhipu entries because they iterate over all `ENV_MAP` and `ALIASES` entries. No new test code is needed in this file. Requires: Config Schema Extension group to be complete.

- [ ] **Add Zhipu integration test to `tests/test_config_generate.py`** — Add a new test function `test_generate_zhipu_provider` to `tests/test_config_generate.py`, following the pattern of the existing `test_generate_full_pipeline` test (lines 126–148). The test should:
  - Use `monkeypatch` to set `NANOBOT_PROVIDERS_ZHIPU_APIKEY` to `"zhipu-test-key-456"` and `NANOBOT_PROVIDERS_ZHIPU_APIBASE` to `"https://api.z.ai/api/coding/paas/v4"`.
  - Use `monkeypatch` to set `HOME` to `tmp_path` and clear all other `NANOBOT_*` env vars.
  - Patch `read_docker_secrets` to a no-op: `monkeypatch.setattr("scripts.config_generate.read_docker_secrets", lambda: None)`.
  - Create `tmp_path / ".nanobot"` directory.
  - Call `generate()`.
  - Load and parse `tmp_path / ".nanobot" / "config.json"`.
  - Assert `config["providers"]["zhipu"]["apiKey"] == "zhipu-test-key-456"`.
  - Assert `config["providers"]["zhipu"]["apiBase"] == "https://api.z.ai/api/coding/paas/v4"`.
  - Assert `config["agents"]["defaults"]["model"] == "anthropic/claude-sonnet-4-5-20250514"` (defaults still applied).
  - Requires: Config Schema Extension group to be complete.

- [ ] **Add Zhipu alias resolution test to `tests/test_config_generate.py`** — Add a new test function `test_resolve_zhipu_alias` to `tests/test_config_generate.py`, following the pattern of the existing `test_resolve_aliases` test (lines 67–71). The test should:
  - Use `monkeypatch.setenv("ZHIPU_API_KEY", "alias-zhipu-key")`.
  - Use `monkeypatch.delenv("NANOBOT_PROVIDERS_ZHIPU_APIKEY", raising=False)`.
  - Call `resolve_aliases()`.
  - Assert `os.environ["NANOBOT_PROVIDERS_ZHIPU_APIKEY"] == "alias-zhipu-key"`.
  - Requires: Config Schema Extension group to be complete.

- [ ] **Run full test suite** — Run `pytest -v` and confirm all tests pass (both existing and new). Fix any failures before proceeding.

## Documentation Update

- [ ] **Add Zhipu to README provider table** — In `README.md`, in the "Provider API Keys" table (lines 39–49), add two new rows after the Groq row and before the Custom rows:
  - `| \`NANOBOT_PROVIDERS_ZHIPU_APIKEY\` | Zhipu AI (Z.AI/GLM) API key | \`ZHIPU_API_KEY\` |`
  - `| \`NANOBOT_PROVIDERS_ZHIPU_APIBASE\` | Zhipu AI API base URL (default: \`https://api.z.ai/api/coding/paas/v4\`) | |`
  - Requires: Config Schema Extension group to be complete.

## Quality Gates

- [ ] **Run pre-commit checks** — Run `pre-commit run --all-files` and fix all errors and warnings until it passes cleanly. This validates formatting, linting, and other project quality rules across all modified files.

- [ ] **Final test run** — Run `pytest -v` one final time to confirm all tests still pass after any pre-commit auto-fixes.
