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

All configuration is driven by environment variables prefixed with `NANOBOT_`. On every container start, the entrypoint runs a config generator that reads these variables and writes `~/.nanobot/config.json`. This means config changes via env vars take effect immediately on restart.

Several common environment variables also have shorter **aliases** for convenience. When both the alias and the canonical variable are set, the canonical variable takes precedence.

### Provider API Keys

| Variable | Description | Alias |
|----------|-------------|-------|
| `NANOBOT_PROVIDERS_OPENROUTER_APIKEY` | OpenRouter API key | `OPENROUTER_API_KEY` |
| `NANOBOT_PROVIDERS_OPENROUTER_APIBASE` | OpenRouter API base URL | |
| `NANOBOT_PROVIDERS_ANTHROPIC_APIKEY` | Anthropic API key | `ANTHROPIC_API_KEY` |
| `NANOBOT_PROVIDERS_ANTHROPIC_APIBASE` | Anthropic API base URL | |
| `NANOBOT_PROVIDERS_OPENAI_APIKEY` | OpenAI API key | `OPENAI_API_KEY` |
| `NANOBOT_PROVIDERS_DEEPSEEK_APIKEY` | DeepSeek API key | `DEEPSEEK_API_KEY` |
| `NANOBOT_PROVIDERS_GROQ_APIKEY` | Groq API key | `GROQ_API_KEY` |
| `NANOBOT_PROVIDERS_ZHIPU_APIKEY` | Zhipu AI (Z.AI/GLM) API key | `ZHIPU_API_KEY` |
| `NANOBOT_PROVIDERS_ZHIPU_APIBASE` | Zhipu AI API base URL (default: `https://api.z.ai/api/coding/paas/v4`) | |
| `NANOBOT_PROVIDERS_CUSTOM_APIKEY` | Custom provider API key | |
| `NANOBOT_PROVIDERS_CUSTOM_APIBASE` | Custom provider API base URL | |

### Agent Config

| Variable | Description | Default | Alias |
|----------|-------------|---------|-------|
| `NANOBOT_AGENTS_DEFAULTS_MODEL` | Default model for agents | `anthropic/claude-sonnet-4-5-20250514` | `NANOBOT_MODEL` |

### Channel Config

| Variable | Description | Type | Alias |
|----------|-------------|------|-------|
| `NANOBOT_CHANNELS_TELEGRAM_ENABLED` | Enable Telegram channel | `bool` | |
| `NANOBOT_CHANNELS_TELEGRAM_TOKEN` | Telegram bot token | `string` | `TELEGRAM_BOT_TOKEN` |
| `NANOBOT_CHANNELS_TELEGRAM_ALLOWFROM` | Allowed Telegram users | `comma-separated list` | |
| `NANOBOT_CHANNELS_DISCORD_ENABLED` | Enable Discord channel | `bool` | |
| `NANOBOT_CHANNELS_DISCORD_TOKEN` | Discord bot token | `string` | |
| `NANOBOT_CHANNELS_DISCORD_ALLOWFROM` | Allowed Discord users | `comma-separated list` | |
| `NANOBOT_CHANNELS_SLACK_ENABLED` | Enable Slack channel | `bool` | |
| `NANOBOT_CHANNELS_SLACK_APPTOKEN` | Slack app token | `string` | |
| `NANOBOT_CHANNELS_SLACK_BOTTOKEN` | Slack bot token | `string` | |
| `NANOBOT_CHANNELS_SLACK_ALLOWFROM` | Allowed Slack users | `comma-separated list` | |
| `NANOBOT_CHANNELS_WHATSAPP_ENABLED` | Enable WhatsApp channel | `bool` | |
| `NANOBOT_CHANNELS_WHATSAPP_ALLOWFROM` | Allowed WhatsApp users | `comma-separated list` | |

### Tools Config

| Variable | Description | Type | Alias |
|----------|-------------|------|-------|
| `NANOBOT_TOOLS_WEB_SEARCH_APIKEY` | Brave Search API key | `string` | `BRAVE_SEARCH_API_KEY` |
| `NANOBOT_TOOLS_MCPSERVERS` | MCP server definitions | `JSON` | |

The `NANOBOT_TOOLS_MCPSERVERS` value should be a JSON object, e.g.:

```
NANOBOT_TOOLS_MCPSERVERS={"server1":{"command":"npx","args":["@modelcontextprotocol/server-filesystem","/data"]}}
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

As an alternative to environment variables, config values can be provided via Docker secrets. Place files in `/run/secrets/` with names matching the `NANOBOT_*` variable names (e.g., `/run/secrets/NANOBOT_PROVIDERS_OPENROUTER_APIKEY`).

The config generator reads secrets on startup and sets them as environment variables. If both a secret and an environment variable exist for the same key, the **environment variable takes precedence**.

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
