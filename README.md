# nanobot-nix

Batteries-included Docker distribution of [Nanobot](https://github.com/HKUDS/nanobot) with Nix self-provisioning.

[![Build](https://github.com/jinglemansweep/nanobot-nix/actions/workflows/build.yml/badge.svg)](https://github.com/jinglemansweep/nanobot-nix/actions/workflows/build.yml)
[![Test](https://github.com/jinglemansweep/nanobot-nix/actions/workflows/test.yml/badge.svg)](https://github.com/jinglemansweep/nanobot-nix/actions/workflows/test.yml)
[![GHCR](https://img.shields.io/badge/ghcr.io-jinglemansweep%2Fnanobot--nix-blue)](https://ghcr.io/jinglemansweep/nanobot-nix)

## Quick Start

1. Copy the example environment file and fill in your values:

   ```bash
   cp .env.example .env
   ```

2. Start the gateway (HTTP API mode):

   ```bash
   docker compose up -d
   ```

3. Or run the interactive CLI:

   ```bash
   docker compose run --rm cli
   ```

See [`.env.example`](.env.example) for all available configuration options.

## Configuration Reference

All configuration is driven by environment variables. Nanobot uses Pydantic `BaseSettings` with `env_prefix="NANOBOT_"` and `env_nested_delimiter="__"`, so all config fields are available as env vars directly. The naming convention is: `NANOBOT_` prefix, `__` (double underscore) between nesting levels, and uppercase snake_case field names (e.g., `NANOBOT_PROVIDERS__ANTHROPIC__API_KEY`).

### Provider API Keys

| Variable | Description |
|----------|-------------|
| `NANOBOT_PROVIDERS__ANTHROPIC__API_KEY` | Anthropic API key |
| `NANOBOT_PROVIDERS__ANTHROPIC__API_BASE` | Anthropic API base URL |
| `NANOBOT_PROVIDERS__OPENAI__API_KEY` | OpenAI API key |
| `NANOBOT_PROVIDERS__OPENAI__API_BASE` | OpenAI API base URL |
| `NANOBOT_PROVIDERS__OPENROUTER__API_KEY` | OpenRouter API key |
| `NANOBOT_PROVIDERS__OPENROUTER__API_BASE` | OpenRouter API base URL |
| `NANOBOT_PROVIDERS__DEEPSEEK__API_KEY` | DeepSeek API key |
| `NANOBOT_PROVIDERS__DEEPSEEK__API_BASE` | DeepSeek API base URL |
| `NANOBOT_PROVIDERS__GROQ__API_KEY` | Groq API key |
| `NANOBOT_PROVIDERS__GROQ__API_BASE` | Groq API base URL |
| `NANOBOT_PROVIDERS__ZHIPU__API_KEY` | Zhipu AI (Z.AI/GLM) API key |
| `NANOBOT_PROVIDERS__ZHIPU__API_BASE` | Zhipu AI API base URL |
| `NANOBOT_PROVIDERS__CUSTOM__API_KEY` | Custom provider API key |
| `NANOBOT_PROVIDERS__CUSTOM__API_BASE` | Custom provider API base URL |

### Agent Config

| Variable | Description |
|----------|-------------|
| `NANOBOT_AGENTS__DEFAULTS__MODEL` | Default model for agents |
| `NANOBOT_AGENTS__DEFAULTS__PROVIDER` | Default provider |
| `NANOBOT_AGENTS__DEFAULTS__MAX_TOKENS` | Max tokens per response |
| `NANOBOT_AGENTS__DEFAULTS__TEMPERATURE` | Sampling temperature |

### Channel Config

| Variable | Description | Type |
|----------|-------------|------|
| `NANOBOT_CHANNELS__TELEGRAM__ENABLED` | Enable Telegram channel | `bool` |
| `NANOBOT_CHANNELS__TELEGRAM__TOKEN` | Telegram bot token | `string` |
| `NANOBOT_CHANNELS__TELEGRAM__ALLOW_FROM` | Allowed Telegram users | `JSON array` |
| `NANOBOT_CHANNELS__DISCORD__ENABLED` | Enable Discord channel | `bool` |
| `NANOBOT_CHANNELS__DISCORD__TOKEN` | Discord bot token | `string` |
| `NANOBOT_CHANNELS__DISCORD__ALLOW_FROM` | Allowed Discord users | `JSON array` |
| `NANOBOT_CHANNELS__SLACK__ENABLED` | Enable Slack channel | `bool` |
| `NANOBOT_CHANNELS__SLACK__APP_TOKEN` | Slack app token | `string` |
| `NANOBOT_CHANNELS__SLACK__BOT_TOKEN` | Slack bot token | `string` |
| `NANOBOT_CHANNELS__EMAIL__ENABLED` | Enable Email channel | `bool` |
| `NANOBOT_CHANNELS__EMAIL__IMAP_HOST` | IMAP server hostname | `string` |
| `NANOBOT_CHANNELS__EMAIL__SMTP_HOST` | SMTP server hostname | `string` |
| `NANOBOT_CHANNELS__EMAIL__ALLOW_FROM` | Allowed email addresses | `JSON array` |
| `NANOBOT_CHANNELS__MATRIX__ENABLED` | Enable Matrix channel | `bool` |
| `NANOBOT_CHANNELS__MATRIX__HOMESERVER` | Matrix homeserver URL | `string` |
| `NANOBOT_CHANNELS__MATRIX__ACCESS_TOKEN` | Matrix access token | `string` |
| `NANOBOT_CHANNELS__MATRIX__ALLOW_FROM` | Allowed Matrix users | `JSON array` |
| `NANOBOT_CHANNELS__WHATSAPP__ENABLED` | Enable WhatsApp channel | `bool` |
| `NANOBOT_CHANNELS__WHATSAPP__ALLOW_FROM` | Allowed WhatsApp users | `JSON array` |

### Tools Config

| Variable | Description | Type |
|----------|-------------|------|
| `NANOBOT_TOOLS__WEB__SEARCH__API_KEY` | Brave Search API key | `string` |
| `NANOBOT_TOOLS__WEB__SEARCH__MAX_RESULTS` | Max search results | `int` |
| `NANOBOT_TOOLS__EXEC__TIMEOUT` | Exec tool timeout | `int` |
| `NANOBOT_TOOLS__RESTRICT_TO_WORKSPACE` | Restrict tools to workspace | `bool` |
| `NANOBOT_TOOLS__MCP_SERVERS` | MCP server definitions | `JSON` |

The `NANOBOT_TOOLS__MCP_SERVERS` value should be a JSON object, e.g.:

```
NANOBOT_TOOLS__MCP_SERVERS={"server1":{"command":"npx","args":["@modelcontextprotocol/server-filesystem","/data"]}}
```

### Nix Config

| Variable | Description |
|----------|-------------|
| `NANOBOT_NIX_ALLOWED_PACKAGES` | Controls which Nix packages the agent can install |

Values for `NANOBOT_NIX_ALLOWED_PACKAGES`:

- `*` — Allow all packages
- `pkg1,pkg2,pkg3` — Allow only the listed packages
- Empty or unset — Deny all package installations

## Custom Skills

Mount a directory of custom skills into the container at `/mnt/skills`:

```yaml
volumes:
  - ./skills:/mnt/skills:ro
```

On startup, the entrypoint symlinks all built-in skills into the workspace, then overlays any custom skills from `/mnt/skills`. Custom skills with the same directory name as a built-in skill will override the built-in version.

Each skill is a directory containing a `SKILL.md` file that defines the skill's behaviour and metadata.

## Nix Self-Provisioning

The container includes [Nix](https://nixos.org/) for on-demand package installation. The agent can install additional tools at runtime without rebuilding the image.

- Packages are installed to the `/nix` volume, which persists across container restarts
- The `NANOBOT_NIX_ALLOWED_PACKAGES` variable controls which packages can be installed (see [Nix Config](#nix-config))
- Pre-installed tools: `git`, `jq`, `tmux`, `curl`, `gh`, `node`, `python3`

To reclaim disk space from unused packages:

```bash
nix-collect-garbage -d
```

## Docker Secrets

As an alternative to environment variables, config values can be provided via Docker secrets. Place files in `/run/secrets/` with names matching the `NANOBOT_*` variable names (e.g., `/run/secrets/NANOBOT_PROVIDERS__ANTHROPIC__API_KEY`).

The entrypoint reads secrets on startup and exports them as environment variables. If both a secret and an environment variable exist for the same key, the **environment variable takes precedence**.

## Building from Source

Using Docker Compose (recommended — uses the build config in `docker-compose.yml`):

```bash
docker compose build
docker compose up --build
```

Or using plain Docker:

```bash
docker build -t nanobot-nix .
```

To pin a specific Nanobot version:

```bash
docker build -t nanobot-nix --build-arg NANOBOT_REF=v0.1.4 .
```

Build arguments:

| Argument | Default | Description |
|----------|---------|-------------|
| `NANOBOT_REPO` | `https://github.com/HKUDS/nanobot.git` | Nanobot Git repository URL |
| `NANOBOT_REF` | `main` | Git ref (branch, tag, or commit) to build |
