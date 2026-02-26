# nanobot-nix — Project Plan (Final)

A batteries-included Docker distribution of [Nanobot](https://github.com/HKUDS/nanobot), built and published via GitHub Actions to GHCR.

---

## All Decisions

| # | Decision |
|---|---|
| 1 | Baseline tools via apt at build time. Nix for agent runtime self-provisioning only. `/nix` as a Docker volume. Container runs read-only. |
| 2 | Single-underscore env vars (`NANOBOT_PROVIDERS_OPENROUTER_APIKEY`) with explicit mapping table to JSON paths. |
| 3 | Hot-reload custom skills via symlinks into workspace. |
| 4 | Single combined skill called **`toolbox`** — covers container environment context + Nix install wrapper usage. |
| 5 | Track upstream `main`. Weekly scheduled builds. |
| 6 | Name: **nanobot-nix** |
| 7 | MCP server config as a single JSON blob env var. |
| 8 | Comma-separated strings auto-converted to JSON arrays by the config generator. |
| 9 | Config mapping isolated in a single declarative data file (`config_schema.py`) — no logic, only data. Generator imports from it and never needs touching for upstream schema changes. |

---

## 1. GitHub Actions CI/CD

- **Triggers**: push to main, tags, weekly schedule (Mon 04:00 UTC), manual dispatch with `nanobot_ref` input
- **Build args**: `NANOBOT_REPO`, `NANOBOT_REF` (default `main`)
- **Multi-arch**: `linux/amd64`, `linux/arm64`
- **Tags**: `latest`, semver, sha, `YYYYMMDD` for scheduled
- **Registry**: `ghcr.io/jinglemansweep/nanobot-nix`
- **Smoke test**: `nanobot status` in built image before push

---

## 2. Dockerfile

### Multi-stage Build

1. **Builder** — clone nanobot at `NANOBOT_REF`, `uv pip install -e .`, build WhatsApp bridge
2. **Runtime** — slim base, apt tools, Node.js 20, Nix (single-user/daemon-less), nanobot, distro scripts/skills

### Apt Baseline (build time)

```
git, jq, tmux, curl, ca-certificates, gnupg, xz-utils, gh
```

### Read-Only Container

Writable volumes only:

| Mount | Purpose |
|---|---|
| `/nix` | Nix store for agent-installed packages |
| `/root/.nanobot` | Workspace, generated config, sessions, memory |
| `/tmp` (tmpfs) | Temporary files |

---

## 3. Environment-Driven Config Generation

### Architecture

Config generation is split into two files with strict separation of concerns:

```
scripts/
├── config_schema.py    # DATA ONLY — mapping table, aliases, array fields, defaults
└── config_generate.py  # LOGIC ONLY — reads env vars, consults schema, writes JSON
```

**`config_schema.py` is the only file that needs editing when upstream nanobot's config format changes.** It contains zero logic — only declarative data structures.

**`config_generate.py` is schema-agnostic.** It imports the four data structures from `config_schema.py` and never needs touching for upstream changes.

### config_schema.py — Data Only

Four declarations, no imports, no functions, no logic:

```python
"""
nanobot-nix config schema

This is the ONLY file that needs updating when upstream nanobot's
config.json structure changes. It contains no logic — only data.

Each entry in ENV_MAP maps a flat environment variable suffix
(after stripping the NANOBOT_ prefix) to a tuple of JSON path
segments representing the target location in config.json.
"""

# ──────────────────────────────────────────────────────────────
# Default config — base structure before any env vars are applied
# ──────────────────────────────────────────────────────────────

DEFAULTS = {
    "agents": {
        "defaults": {
            "model": "anthropic/claude-sonnet-4-5-20250514"
        }
    }
}

# ──────────────────────────────────────────────────────────────
# Env var mapping — NANOBOT_{suffix} → JSON path tuple
# ──────────────────────────────────────────────────────────────

ENV_MAP = {
    # Providers
    "PROVIDERS_OPENROUTER_APIKEY":       ("providers", "openrouter", "apiKey"),
    "PROVIDERS_OPENROUTER_APIBASE":      ("providers", "openrouter", "apiBase"),
    "PROVIDERS_ANTHROPIC_APIKEY":        ("providers", "anthropic", "apiKey"),
    "PROVIDERS_ANTHROPIC_APIBASE":       ("providers", "anthropic", "apiBase"),
    "PROVIDERS_OPENAI_APIKEY":           ("providers", "openai", "apiKey"),
    "PROVIDERS_DEEPSEEK_APIKEY":         ("providers", "deepseek", "apiKey"),
    "PROVIDERS_GROQ_APIKEY":             ("providers", "groq", "apiKey"),
    "PROVIDERS_CUSTOM_APIKEY":           ("providers", "custom", "apiKey"),
    "PROVIDERS_CUSTOM_APIBASE":          ("providers", "custom", "apiBase"),

    # Agent defaults
    "AGENTS_DEFAULTS_MODEL":             ("agents", "defaults", "model"),

    # Channels — Telegram
    "CHANNELS_TELEGRAM_ENABLED":         ("channels", "telegram", "enabled"),
    "CHANNELS_TELEGRAM_TOKEN":           ("channels", "telegram", "token"),
    "CHANNELS_TELEGRAM_ALLOWFROM":       ("channels", "telegram", "allowFrom"),

    # Channels — Discord
    "CHANNELS_DISCORD_ENABLED":          ("channels", "discord", "enabled"),
    "CHANNELS_DISCORD_TOKEN":            ("channels", "discord", "token"),
    "CHANNELS_DISCORD_ALLOWFROM":        ("channels", "discord", "allowFrom"),

    # Channels — Slack
    "CHANNELS_SLACK_ENABLED":            ("channels", "slack", "enabled"),
    "CHANNELS_SLACK_APPTOKEN":           ("channels", "slack", "appToken"),
    "CHANNELS_SLACK_BOTTOKEN":           ("channels", "slack", "botToken"),
    "CHANNELS_SLACK_ALLOWFROM":          ("channels", "slack", "allowFrom"),

    # Channels — WhatsApp
    "CHANNELS_WHATSAPP_ENABLED":         ("channels", "whatsapp", "enabled"),
    "CHANNELS_WHATSAPP_ALLOWFROM":       ("channels", "whatsapp", "allowFrom"),

    # Tools — Web search
    "TOOLS_WEB_SEARCH_APIKEY":           ("tools", "web", "search", "apiKey"),

    # Tools — MCP servers (JSON blob)
    "TOOLS_MCPSERVERS":                  ("tools", "mcpServers"),
}

# ──────────────────────────────────────────────────────────────
# Array fields — comma-separated string → JSON array conversion.
# Values already starting with [ are parsed as JSON literals.
# ──────────────────────────────────────────────────────────────

ARRAY_FIELDS = {
    "CHANNELS_TELEGRAM_ALLOWFROM",
    "CHANNELS_DISCORD_ALLOWFROM",
    "CHANNELS_SLACK_ALLOWFROM",
    "CHANNELS_WHATSAPP_ALLOWFROM",
}

# ──────────────────────────────────────────────────────────────
# Shorthand aliases — convenient env var → canonical NANOBOT_ var.
# If both alias and canonical are set, canonical wins.
# ──────────────────────────────────────────────────────────────

ALIASES = {
    "OPENROUTER_API_KEY":   "NANOBOT_PROVIDERS_OPENROUTER_APIKEY",
    "ANTHROPIC_API_KEY":    "NANOBOT_PROVIDERS_ANTHROPIC_APIKEY",
    "OPENAI_API_KEY":       "NANOBOT_PROVIDERS_OPENAI_APIKEY",
    "DEEPSEEK_API_KEY":     "NANOBOT_PROVIDERS_DEEPSEEK_APIKEY",
    "GROQ_API_KEY":         "NANOBOT_PROVIDERS_GROQ_APIKEY",
    "NANOBOT_MODEL":        "NANOBOT_AGENTS_DEFAULTS_MODEL",
    "TELEGRAM_BOT_TOKEN":   "NANOBOT_CHANNELS_TELEGRAM_TOKEN",
    "BRAVE_SEARCH_API_KEY": "NANOBOT_TOOLS_WEB_SEARCH_APIKEY",
}
```

### config_generate.py — Logic Only

Responsibilities (imports everything from `config_schema`):

1. Deep-copy `DEFAULTS` as base config
2. Scan env for `ALIASES` → set as canonical `NANOBOT_*` if canonical not already present
3. Scan env for `NANOBOT_*` vars → strip prefix → look up in `ENV_MAP`
4. Unknown keys → log warning, skip
5. Infer value type:
   - `true`/`false` → bool
   - Parseable int/float → number
   - Starts with `[` or `{` → parse as JSON literal
   - Key in `ARRAY_FIELDS` and value contains commas → split, trim → list of strings
   - Else → string
6. Set value at JSON path in config dict
7. Write `~/.nanobot/config.json`

**This file contains zero knowledge of nanobot's config structure.** All schema awareness is in `config_schema.py`.

### Schema Update Workflow

When upstream nanobot adds or changes config keys:

1. Edit `scripts/config_schema.py` only
2. Add/modify entries in `ENV_MAP`, `ARRAY_FIELDS`, `ALIASES`, or `DEFAULTS`
3. Update `.env.example` if new user-facing vars were added
4. No changes to `config_generate.py`, `entrypoint.sh`, or any other file

---

## 4. Skills Architecture

### Two Directories

| Path | Source | Writable | Purpose |
|---|---|---|---|
| `/opt/nanobot-nix/skills/` | Baked into image | No | Built-in distro skills |
| `/mnt/skills/` | Bind-mounted at runtime | No (`:ro`) | User custom skills |

### Injection via Symlinks

Entrypoint symlinks contents of both into `~/.nanobot/workspace/skills/`. Custom skills override built-in skills of the same name. Symlinks mean changes to bind-mounted skills are immediately visible — hot-reload works through the filesystem.

### Built-in: `toolbox` (alwaysLoad: true)

Single skill covering:

**Container environment context:**
- Running inside a read-only Docker container
- Writable paths: `/root/.nanobot` (workspace volume), `/nix` (package store volume), `/tmp` (tmpfs)
- Pre-installed tools: git, jq, tmux, curl, gh, Node.js 20
- Nix package manager available for additional tools

**Self-provisioning instructions:**
- How to call `/opt/nanobot-nix/scripts/nix-install.sh <package>`
- Check `which <tool>` before installing
- How to search: `/opt/nanobot-nix/scripts/nix-search.sh <query>`
- Common package name → command name mappings
- Whitelist denial handling
- Persistence behaviour

### Custom Skills Mount

```yaml
volumes:
  - ./my-skills:/mnt/skills:ro
```

---

## 5. Nix Wrapper Scripts

### `nix-install.sh`

Whitelist via `NANOBOT_NIX_ALLOWED_PACKAGES`:

| Value | Behaviour |
|---|---|
| `gh,ripgrep,fd,playwright` | Only these allowed |
| `*` | Allow any |
| Empty/unset | Deny all |

### `nix-search.sh`

```bash
/opt/nanobot-nix/scripts/nix-search.sh <query>
```

---

## 6. Entrypoint Flow

```
entrypoint.sh
│
├─ 1. Source Nix profile
│
├─ 2. nanobot onboard (if no workspace yet)
│
├─ 3. config_generate.py (imports config_schema.py)
│     ├─ Load DEFAULTS from schema
│     ├─ Resolve ALIASES from schema
│     ├─ Parse NANOBOT_* via ENV_MAP from schema
│     ├─ Infer types, split arrays via ARRAY_FIELDS from schema
│     ├─ Warn on unknown keys
│     └─ Write ~/.nanobot/config.json
│
├─ 4. Inject skills
│     ├─ Symlink /opt/nanobot-nix/skills/*  → workspace/skills/
│     └─ Symlink /mnt/skills/*              → workspace/skills/
│
└─ 5. exec nanobot "$@"
```

---

## 7. Docker Compose

```yaml
services:
  gateway:
    image: ghcr.io/jinglemansweep/nanobot-nix:latest
    command: ["gateway"]
    restart: unless-stopped
    read_only: true
    ports: ["18790:18790"]
    env_file: .env
    tmpfs:
      - /tmp
    volumes:
      - nanobot-data:/root/.nanobot
      - nix-store:/nix
      - ./skills:/mnt/skills:ro

  cli:
    image: ghcr.io/jinglemansweep/nanobot-nix:latest
    profiles: [cli]
    command: ["agent"]
    stdin_open: true
    tty: true
    read_only: true
    env_file: .env
    tmpfs:
      - /tmp
    volumes:
      - nanobot-data:/root/.nanobot
      - nix-store:/nix
      - ./skills:/mnt/skills:ro

volumes:
  nanobot-data:
  nix-store:
```

---

## 8. File Structure

```
nanobot-nix/
├── .github/
│   └── workflows/
│       └── build.yml
├── scripts/
│   ├── entrypoint.sh              # Orchestrates startup
│   ├── config_schema.py           # DATA ONLY — the only file to edit for schema changes
│   ├── config_generate.py         # LOGIC ONLY — schema-agnostic generator
│   ├── nix-install.sh             # Whitelisted package installer
│   └── nix-search.sh              # Package search helper
├── skills/
│   └── toolbox/
│       └── SKILL.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── LICENSE
└── README.md
```
