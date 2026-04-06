# Research

> Source: `plans/01-config-expansion/00-initial/PROMPT.md`

## Nanobot Upstream Config Schema

- **URL:** https://github.com/HKUDS/nanobot/blob/main/nanobot/config/schema.py
- **Status:** Actively maintained
- **Latest Version:** N/A (main branch, Pydantic-based schema)
- **Compatibility:** Direct upstream dependency — Nanobot reads env vars natively via Pydantic BaseSettings
- **Key Findings:**
  - Schema uses Pydantic `BaseSettings` with `env_prefix="NANOBOT_"` and `env_nested_delimiter="__"`
  - Field names use camelCase aliases via `to_camel` generator (snake_case in Python, camelCase in JSON)
  - Root config has 5 top-level sections: `agents`, `channels`, `providers`, `gateway`, `tools`
  - **Providers:** 16 providers defined (we mapped 7): custom, anthropic, openai, openrouter, deepseek, groq, zhipu, dashscope, vllm, gemini, moonshot, minimax, aihubmix, siliconflow, volcengine, openai_codex, github_copilot
  - **Each provider** has 3 fields: `api_key`, `api_base`, `extra_headers`
  - **Channels:** 10 channels defined (we partially mapped 4): whatsapp, telegram, discord, feishu, mochat, dingtalk, email, slack, qq, matrix
  - **Channel-level settings:** `send_progress` and `send_tool_hints`
  - **Agent defaults:** 7 fields (we mapped 1): workspace, model, provider, max_tokens, temperature, max_tool_iterations, memory_window
  - **Gateway:** host, port, heartbeat.enabled, heartbeat.interval_s
  - **Tools:** web.search.max_results, exec.timeout, exec.path_append, restrict_to_workspace, plus web.search.api_key and mcp_servers
  - Mochat channel has deeply nested config (mention sub-object, groups dict)
  - Slack has nested `dm` sub-config with its own `enabled`, `policy`, `allow_from`
  - Matrix has `group_policy`, `group_allow_from`, `allow_room_mentions` fields

## Pydantic Native Env Var Support

**Key discovery:** Nanobot's Pydantic `BaseSettings` with `env_prefix="NANOBOT_"` and `env_nested_delimiter="__"` means every config field is already accessible as an env var without any custom mapping.

### Naming Convention

Pydantic uses **snake_case field names** (not camelCase aliases) for env var resolution:

- Python field `api_key` on provider `anthropic` → `NANOBOT_PROVIDERS__ANTHROPIC__API_KEY`
- Python field `token` on channel `telegram` → `NANOBOT_CHANNELS__TELEGRAM__TOKEN`
- Python field `allow_from` on channel `telegram` → `NANOBOT_CHANNELS__TELEGRAM__ALLOW_FROM`
- Python field `max_tokens` on agent defaults → `NANOBOT_AGENTS__DEFAULTS__MAX_TOKENS`
- Python field `interval_s` on gateway heartbeat → `NANOBOT_GATEWAY__HEARTBEAT__INTERVAL_S`

The delimiter is `__` (double underscore) between each nesting level. Field names are uppercased.

### Verified Upstream Field Names (fetched from schema.py)

**Provider fields** (all 17 providers share the same fields):
- `api_key`, `api_base`, `extra_headers`

**Agent defaults:**
- `workspace`, `model`, `provider`, `max_tokens`, `temperature`, `max_tool_iterations`, `memory_window`

**Channel-level settings** (on `ChannelsConfig`):
- `send_progress`, `send_tool_hints`

**Telegram:** `enabled`, `token`, `allow_from`, `proxy`, `reply_to_message`
**Discord:** `enabled`, `token`, `allow_from`, `gateway_url`, `intents`
**WhatsApp:** `enabled`, `bridge_url`, `bridge_token`, `allow_from`
**Slack:** `enabled`, `mode`, `webhook_path`, `bot_token`, `app_token`, `user_token_read_only`, `reply_in_thread`, `react_emoji`, `group_policy`, `group_allow_from`, `dm` (nested: `enabled`, `policy`, `allow_from`) — **Note: no top-level `allow_from` on Slack**
**Email:** `enabled`, `consent_granted`, `imap_host`, `imap_port`, `imap_username`, `imap_password`, `imap_mailbox`, `imap_use_ssl`, `smtp_host`, `smtp_port`, `smtp_username`, `smtp_password`, `smtp_use_tls`, `smtp_use_ssl`, `from_address`, `auto_reply_enabled`, `poll_interval_seconds`, `mark_seen`, `max_body_chars`, `subject_prefix`, `allow_from`
**Feishu:** `enabled`, `app_id`, `app_secret`, `encrypt_key`, `verification_token`, `allow_from`
**DingTalk:** `enabled`, `client_id`, `client_secret`, `allow_from`
**Matrix:** `enabled`, `homeserver`, `access_token`, `user_id`, `device_id`, `e2ee_enabled`, `sync_stop_grace_seconds`, `max_media_bytes`, `allow_from`, `group_policy`, `group_allow_from`, `allow_room_mentions`
**QQ:** `enabled`, `app_id`, `secret`, `allow_from`
**Mochat:** `enabled`, `base_url`, `socket_url`, `socket_path`, `socket_disable_msgpack`, `socket_reconnect_delay_ms`, `socket_max_reconnect_delay_ms`, `socket_connect_timeout_ms`, `refresh_interval_ms`, `watch_timeout_ms`, `watch_limit`, `retry_delay_ms`, `max_retry_attempts`, `claw_token`, `agent_user_id`, `sessions`, `panels`, `allow_from`, `mention` (nested: `require_in_groups`), `groups` (dict), `reply_delay_mode`, `reply_delay_ms`

**Gateway:** `host`, `port`, `heartbeat` (nested: `enabled`, `interval_s`)
**Tools:** `web` (nested: `search.api_key`, `search.max_results`), `exec` (nested: `timeout`, `path_append`), `restrict_to_workspace`, `mcp_servers`

### Type Handling

| Type | Pydantic behaviour | Example |
|------|-------------------|---------|
| `str` | Direct passthrough | `NANOBOT_PROVIDERS__ANTHROPIC__API_KEY=sk-abc` |
| `bool` | Parses `true`/`false`/`1`/`0` natively | `NANOBOT_CHANNELS__TELEGRAM__ENABLED=true` |
| `int` | Parses integer strings natively | `NANOBOT_GATEWAY__PORT=8080` |
| `float` | Parses float strings natively | `NANOBOT_AGENTS__DEFAULTS__TEMPERATURE=0.7` |
| `list[str]` | Requires JSON array syntax | `NANOBOT_CHANNELS__TELEGRAM__ALLOW_FROM=["user1","user2"]` |
| `dict[str, str]` | Requires JSON object syntax | `NANOBOT_PROVIDERS__ANTHROPIC__EXTRA_HEADERS={"X-Key":"val"}` |
| `dict` (complex) | Requires JSON object syntax | `NANOBOT_TOOLS__MCP_SERVERS={"srv":{"command":"npx"}}` |

### Comparison: Old Mapping Layer vs Pydantic Native

| Feature | Old mapping layer | Pydantic native |
|---------|------------------|-----------------|
| Prefix | `NANOBOT_` (flat) | `NANOBOT_` + `__` delimiter |
| Delimiter | Single `_` | Double `__` |
| Field naming | camelCase-derived UPPER_SNAKE | snake_case-derived UPPER_SNAKE |
| List parsing | CSV (`user1,user2`) | JSON (`["user1","user2"]`) |
| Dict parsing | JSON (same) | JSON (same) |
| Bool parsing | Custom `infer_type()` | Pydantic native |
| Int/float parsing | Custom `infer_type()` | Pydantic native |
| Aliases | Custom `ALIASES` dict | None (use canonical names) |
| Defaults | Custom `DEFAULTS` dict | Upstream defaults apply |
| Config output | Writes `config.json` | Reads env vars at runtime |
| Coverage | Partial (mapped fields only) | Complete (all fields) |
| Maintenance | Manual sync with upstream | Zero maintenance |

### NANOBOT_NIX_ALLOWED_PACKAGES Safety

`NANOBOT_NIX_ALLOWED_PACKAGES` is consumed by `scripts/nix-install.sh`, not by Pydantic. It is safe because:

- Pydantic's `env_nested_delimiter="__"` means it only interprets env vars with `__` separators as nested config paths
- `NANOBOT_NIX_ALLOWED_PACKAGES` has no `__` delimiter, so Pydantic sees it as a single top-level field `nix_allowed_packages`
- There is no matching field in the upstream schema, so Pydantic ignores it (BaseSettings ignores unknown fields by default)
