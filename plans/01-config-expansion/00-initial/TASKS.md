# Task List

> Source: `plans/01-config-expansion/00-initial/PLAN.md`

## Deletions — Remove Mapping Layer

### Python Modules

- [x] **Delete `scripts/config_schema.py`** — Remove the file `scripts/config_schema.py`. This file contains `ENV_MAP`, `DEFAULTS`, `ARRAY_FIELDS`, and `ALIASES` — all redundant now that Pydantic handles env vars natively. Verify: `ls scripts/config_schema.py` returns "No such file".

- [x] **Delete `scripts/config_generate.py`** — Remove the file `scripts/config_generate.py`. This file contains the custom config generation pipeline that writes `~/.nanobot/config.json` from env vars. No longer needed. Verify: `ls scripts/config_generate.py` returns "No such file".

- [x] **Delete `scripts/__init__.py`** — Remove the file `scripts/__init__.py`. This was the Python package init for `scripts/`. No Python modules remain in `scripts/` after the above deletions (only shell scripts remain: `entrypoint.sh`, `link-skills.sh`, `nix-install.sh`). Verify: `ls scripts/__init__.py` returns "No such file".

### Tests for Deleted Modules

- [x] **Delete `tests/test_config_schema.py`** — Remove the file `tests/test_config_schema.py`. These tests cover the deleted `config_schema.py` module. Verify: `ls tests/test_config_schema.py` returns "No such file".

- [x] **Delete `tests/test_config_generate.py`** — Remove the file `tests/test_config_generate.py`. These tests cover the deleted `config_generate.py` module. Verify: `ls tests/test_config_generate.py` returns "No such file".

## Entrypoint — Docker Secrets Shell Loop

- [ ] **Replace Python config generator call in `scripts/entrypoint.sh`** — In `scripts/entrypoint.sh`, replace line 16 (`python3 -m scripts.config_generate`) with a shell-based Docker secrets export loop. The new Step 3 should be:
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
  This preserves the existing behaviour: env vars take precedence over secrets (the `if [ -z "${!name:-}" ]` check skips secrets when the env var is already set). Also update the step comment from "Step 3: Config generation" to "Step 3: Docker secrets → env vars". Renumber subsequent steps: "Step 4: Inject skills" and "Step 5: Exec nanobot" remain unchanged (they are already numbered 4 and 5). Verify: run `bash -n scripts/entrypoint.sh` to confirm no syntax errors.

## Build Config

- [ ] **Remove `scripts*` from setuptools package find in `pyproject.toml`** — In `pyproject.toml`, change the `[tool.setuptools.packages.find]` section. The current content is `include = ["scripts*"]`. Since no Python packages remain in `scripts/`, remove the entire `[tool.setuptools.packages.find]` section (both the header line and the `include = ["scripts*"]` line). Keep `[project.optional-dependencies] dev = ["pytest"]` intact since `tests/test_link_skills.py` and `tests/test_nix_install.py` remain. Verify: `python3 -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"` succeeds and the output has no `tool.setuptools.packages.find` key.

## Documentation — `.env.example`

- [ ] **Rewrite `.env.example` with native Pydantic env var format** — Replace the entire contents of `.env.example` with the new format. All env vars must use the `NANOBOT_` prefix with `__` (double underscore) nested delimiter and snake_case-derived field names (uppercased). Remove all alias comments (e.g., `# Alias: OPENROUTER_API_KEY`). Change list type hints from "Comma-separated list" to "JSON array" (e.g., `["user1","user2"]`). Keep the `NANOBOT_NIX_ALLOWED_PACKAGES` section unchanged (it uses single `_`, consumed by `nix-install.sh`, not Pydantic). The file should contain these sections:
  - [ ] **Header** — File header comment explaining this is nanobot-nix env config, copy to `.env`, all variables optional. Note the naming convention: `NANOBOT_` prefix, `__` nested delimiter, uppercase snake_case field names.
  - [ ] **Provider API Keys** — Include all 17 providers from the upstream schema. Each provider has 3 fields: `api_key`, `api_base`, `extra_headers`. Group commonly used providers first (anthropic, openai, openrouter, deepseek, groq), then remaining providers. Format: `NANOBOT_PROVIDERS__<PROVIDER>__API_KEY=`, `NANOBOT_PROVIDERS__<PROVIDER>__API_BASE=`, `NANOBOT_PROVIDERS__<PROVIDER>__EXTRA_HEADERS=` with comment `# JSON object`. Only include `API_KEY` and `API_BASE` for each provider (skip `EXTRA_HEADERS` for brevity, but mention it in a comment at the top of the section).
  - [ ] **Agent Defaults** — Include all 7 agent default fields: `NANOBOT_AGENTS__DEFAULTS__MODEL=`, `NANOBOT_AGENTS__DEFAULTS__PROVIDER=`, `NANOBOT_AGENTS__DEFAULTS__WORKSPACE=`, `NANOBOT_AGENTS__DEFAULTS__MAX_TOKENS=`, `NANOBOT_AGENTS__DEFAULTS__TEMPERATURE=`, `NANOBOT_AGENTS__DEFAULTS__MAX_TOOL_ITERATIONS=`, `NANOBOT_AGENTS__DEFAULTS__MEMORY_WINDOW=`. Add type hints as comments (e.g., `# int`, `# float`).
  - [ ] **Channel-level Settings** — `NANOBOT_CHANNELS__SEND_PROGRESS=` and `NANOBOT_CHANNELS__SEND_TOOL_HINTS=` with `# bool` comment.
  - [ ] **Telegram** — `NANOBOT_CHANNELS__TELEGRAM__ENABLED=`, `NANOBOT_CHANNELS__TELEGRAM__TOKEN=`, `NANOBOT_CHANNELS__TELEGRAM__ALLOW_FROM=` with comment `# JSON array (e.g. ["user1","user2"])`, `NANOBOT_CHANNELS__TELEGRAM__PROXY=`, `NANOBOT_CHANNELS__TELEGRAM__REPLY_TO_MESSAGE=` with `# bool`.
  - [ ] **Discord** — `NANOBOT_CHANNELS__DISCORD__ENABLED=`, `NANOBOT_CHANNELS__DISCORD__TOKEN=`, `NANOBOT_CHANNELS__DISCORD__ALLOW_FROM=` with JSON array comment, `NANOBOT_CHANNELS__DISCORD__GATEWAY_URL=`, `NANOBOT_CHANNELS__DISCORD__INTENTS=` with `# int`.
  - [ ] **Slack** — `NANOBOT_CHANNELS__SLACK__ENABLED=`, `NANOBOT_CHANNELS__SLACK__MODE=`, `NANOBOT_CHANNELS__SLACK__WEBHOOK_PATH=`, `NANOBOT_CHANNELS__SLACK__BOT_TOKEN=`, `NANOBOT_CHANNELS__SLACK__APP_TOKEN=`, `NANOBOT_CHANNELS__SLACK__USER_TOKEN_READ_ONLY=`, `NANOBOT_CHANNELS__SLACK__REPLY_IN_THREAD=` (`# bool`), `NANOBOT_CHANNELS__SLACK__REACT_EMOJI=`, `NANOBOT_CHANNELS__SLACK__GROUP_POLICY=`, `NANOBOT_CHANNELS__SLACK__GROUP_ALLOW_FROM=` (JSON array), `NANOBOT_CHANNELS__SLACK__DM__ENABLED=` (`# bool`), `NANOBOT_CHANNELS__SLACK__DM__POLICY=`, `NANOBOT_CHANNELS__SLACK__DM__ALLOW_FROM=` (JSON array). Note: Slack has no top-level `allow_from`.
  - [ ] **WhatsApp** — `NANOBOT_CHANNELS__WHATSAPP__ENABLED=`, `NANOBOT_CHANNELS__WHATSAPP__BRIDGE_URL=`, `NANOBOT_CHANNELS__WHATSAPP__BRIDGE_TOKEN=`, `NANOBOT_CHANNELS__WHATSAPP__ALLOW_FROM=` (JSON array).
  - [ ] **Email** — `NANOBOT_CHANNELS__EMAIL__ENABLED=`, `NANOBOT_CHANNELS__EMAIL__CONSENT_GRANTED=` (`# bool`), IMAP fields (`IMAP_HOST`, `IMAP_PORT`, `IMAP_USERNAME`, `IMAP_PASSWORD`, `IMAP_MAILBOX`, `IMAP_USE_SSL`), SMTP fields (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS`, `SMTP_USE_SSL`), `FROM_ADDRESS`, `AUTO_REPLY_ENABLED` (`# bool`), `POLL_INTERVAL_SECONDS` (`# int`), `MARK_SEEN` (`# bool`), `MAX_BODY_CHARS` (`# int`), `SUBJECT_PREFIX`, `ALLOW_FROM` (JSON array). All prefixed with `NANOBOT_CHANNELS__EMAIL__`.
  - [ ] **Matrix** — `NANOBOT_CHANNELS__MATRIX__ENABLED=`, `HOMESERVER`, `ACCESS_TOKEN`, `USER_ID`, `DEVICE_ID`, `E2EE_ENABLED` (`# bool`), `SYNC_STOP_GRACE_SECONDS` (`# int`), `MAX_MEDIA_BYTES` (`# int`), `ALLOW_FROM` (JSON array), `GROUP_POLICY`, `GROUP_ALLOW_FROM` (JSON array), `ALLOW_ROOM_MENTIONS` (`# bool`). All prefixed with `NANOBOT_CHANNELS__MATRIX__`.
  - [ ] **Other Channels** — Brief sections for Feishu (`APP_ID`, `APP_SECRET`, `ENCRYPT_KEY`, `VERIFICATION_TOKEN`, `ALLOW_FROM`), DingTalk (`CLIENT_ID`, `CLIENT_SECRET`, `ALLOW_FROM`), QQ (`APP_ID`, `SECRET`, `ALLOW_FROM`), Mochat (comment noting complex config, reference upstream docs, include `BASE_URL`, `CLAW_TOKEN`, `AGENT_USER_ID`). All with `NANOBOT_CHANNELS__<CHANNEL>__` prefix.
  - [ ] **Gateway** — `NANOBOT_GATEWAY__HOST=`, `NANOBOT_GATEWAY__PORT=` (`# int`), `NANOBOT_GATEWAY__HEARTBEAT__ENABLED=` (`# bool`), `NANOBOT_GATEWAY__HEARTBEAT__INTERVAL_S=` (`# int`).
  - [ ] **Tools** — `NANOBOT_TOOLS__WEB__SEARCH__API_KEY=`, `NANOBOT_TOOLS__WEB__SEARCH__MAX_RESULTS=` (`# int`), `NANOBOT_TOOLS__EXEC__TIMEOUT=` (`# int`), `NANOBOT_TOOLS__EXEC__PATH_APPEND=`, `NANOBOT_TOOLS__RESTRICT_TO_WORKSPACE=` (`# bool`), `NANOBOT_TOOLS__MCP_SERVERS=` with comment `# JSON object (e.g. {"server1":{"command":"npx","args":[...]}})`.
  - [ ] **Nix Config** — Keep `NANOBOT_NIX_ALLOWED_PACKAGES=` section exactly as-is (single `_` delimiter, consumed by `nix-install.sh`).

## Documentation — `README.md`

- [ ] **Rewrite Configuration Reference section in `README.md`** — Replace the Configuration Reference section (lines 31–99) in `README.md`. The new section should:
  - [ ] **Update intro paragraph** — Replace lines 33–36. Remove reference to "config generator that writes `~/.nanobot/config.json`". New text: explain that Nanobot uses Pydantic `BaseSettings` with `env_prefix="NANOBOT_"` and `env_nested_delimiter="__"`, so all config fields are available as env vars directly. Mention the naming convention: `NANOBOT_` prefix, `__` between nesting levels, uppercase snake_case field names. Remove all alias references.
  - [ ] **Update Provider API Keys table** — Replace lines 37–51. Remove the "Alias" column. Update all env var names to `__` delimiter format: `NANOBOT_PROVIDERS__OPENROUTER__API_KEY`, `NANOBOT_PROVIDERS__ANTHROPIC__API_KEY`, `NANOBOT_PROVIDERS__OPENAI__API_KEY`, etc. Include all commonly used providers.
  - [ ] **Update Agent Config table** — Replace lines 53–57. Remove the "Alias" column and "Default" column. Change `NANOBOT_AGENTS_DEFAULTS_MODEL` to `NANOBOT_AGENTS__DEFAULTS__MODEL`. Add other agent defaults fields: `PROVIDER`, `MAX_TOKENS`, `TEMPERATURE`.
  - [ ] **Update Channel Config table** — Replace lines 59–74. Remove the "Alias" column. Update all env var names to `__` delimiter format (e.g., `NANOBOT_CHANNELS__TELEGRAM__TOKEN`). Change type "comma-separated list" to "JSON array". Add Email and Matrix channels. Note that Slack has no top-level `allow_from`.
  - [ ] **Update Tools Config table** — Replace lines 76–87. Update env var names: `NANOBOT_TOOLS__WEB__SEARCH__API_KEY` (was `NANOBOT_TOOLS_WEB_SEARCH_APIKEY`), `NANOBOT_TOOLS__MCP_SERVERS` (was `NANOBOT_TOOLS_MCPSERVERS`). Remove the "Alias" column. Update the MCP servers JSON example to use `__` delimiter name.
  - [ ] **Update Docker Secrets section** — Replace lines 128–132. Update the example secret file name from `NANOBOT_PROVIDERS_OPENROUTER_APIKEY` to `NANOBOT_PROVIDERS__ANTHROPIC__API_KEY`. Change "config generator reads secrets" to "entrypoint reads secrets and exports them as environment variables". Keep the precedence note (env vars take precedence over secrets).

## Validation

- [ ] **Run remaining tests** — Execute `source .venv/bin/activate && pytest` to run the remaining test suite (`tests/test_link_skills.py` and `tests/test_nix_install.py`). Both must pass. If any test imports from deleted modules, the test file has a stale import that needs fixing. Verify: `pytest` exits with code 0 and all tests pass.

- [ ] **Run pre-commit quality gates** — Execute `source .venv/bin/activate && pre-commit run --all-files`. Fix any errors or warnings until the entire suite passes cleanly. Common issues: trailing whitespace in new/modified files, shellcheck warnings in `entrypoint.sh`, YAML/TOML formatting. Verify: `pre-commit run --all-files` exits with code 0.
