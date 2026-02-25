# Task List

> Source: `.agent/plans/01-initial/PLAN.md`

## Project Foundation

- [x] **Create `.gitignore`** — Create `.gitignore` at the repository root with rules covering: `.env`, `__pycache__/`, `*.pyc`, `node_modules/`, `.DS_Store`, `*.swp`, `*.swo`, `.idea/`, `.vscode/`, `*.log`. Verify by running `git status` and confirming no ignored-pattern files appear.

## Config Generation

### Config Schema

- [x] **Create `scripts/config_schema.py`** — Create the file `scripts/config_schema.py` containing exactly four top-level declarations and no imports, functions, or logic. Copy the complete content from the PROMPT.md/PLAN.md specification:
  - [x] `DEFAULTS` dict — `{"agents": {"defaults": {"model": "anthropic/claude-sonnet-4-5-20250514"}}}`.
  - [x] `ENV_MAP` dict — All entries mapping `NANOBOT_*` suffixes to JSON path tuples. Include: `PROVIDERS_OPENROUTER_APIKEY` → `("providers", "openrouter", "apiKey")`, `PROVIDERS_OPENROUTER_APIBASE` → `("providers", "openrouter", "apiBase")`, `PROVIDERS_ANTHROPIC_APIKEY` → `("providers", "anthropic", "apiKey")`, `PROVIDERS_ANTHROPIC_APIBASE` → `("providers", "anthropic", "apiBase")`, `PROVIDERS_OPENAI_APIKEY` → `("providers", "openai", "apiKey")`, `PROVIDERS_DEEPSEEK_APIKEY` → `("providers", "deepseek", "apiKey")`, `PROVIDERS_GROQ_APIKEY` → `("providers", "groq", "apiKey")`, `PROVIDERS_CUSTOM_APIKEY` → `("providers", "custom", "apiKey")`, `PROVIDERS_CUSTOM_APIBASE` → `("providers", "custom", "apiBase")`, `AGENTS_DEFAULTS_MODEL` → `("agents", "defaults", "model")`, `CHANNELS_TELEGRAM_ENABLED` → `("channels", "telegram", "enabled")`, `CHANNELS_TELEGRAM_TOKEN` → `("channels", "telegram", "token")`, `CHANNELS_TELEGRAM_ALLOWFROM` → `("channels", "telegram", "allowFrom")`, `CHANNELS_DISCORD_ENABLED` → `("channels", "discord", "enabled")`, `CHANNELS_DISCORD_TOKEN` → `("channels", "discord", "token")`, `CHANNELS_DISCORD_ALLOWFROM` → `("channels", "discord", "allowFrom")`, `CHANNELS_SLACK_ENABLED` → `("channels", "slack", "enabled")`, `CHANNELS_SLACK_APPTOKEN` → `("channels", "slack", "appToken")`, `CHANNELS_SLACK_BOTTOKEN` → `("channels", "slack", "botToken")`, `CHANNELS_SLACK_ALLOWFROM` → `("channels", "slack", "allowFrom")`, `CHANNELS_WHATSAPP_ENABLED` → `("channels", "whatsapp", "enabled")`, `CHANNELS_WHATSAPP_ALLOWFROM` → `("channels", "whatsapp", "allowFrom")`, `TOOLS_WEB_SEARCH_APIKEY` → `("tools", "web", "search", "apiKey")`, `TOOLS_MCPSERVERS` → `("tools", "mcpServers")`.
  - [x] `ARRAY_FIELDS` set — `{"CHANNELS_TELEGRAM_ALLOWFROM", "CHANNELS_DISCORD_ALLOWFROM", "CHANNELS_SLACK_ALLOWFROM", "CHANNELS_WHATSAPP_ALLOWFROM"}`.
  - [x] `ALIASES` dict — `{"OPENROUTER_API_KEY": "NANOBOT_PROVIDERS_OPENROUTER_APIKEY", "ANTHROPIC_API_KEY": "NANOBOT_PROVIDERS_ANTHROPIC_APIKEY", "OPENAI_API_KEY": "NANOBOT_PROVIDERS_OPENAI_APIKEY", "DEEPSEEK_API_KEY": "NANOBOT_PROVIDERS_DEEPSEEK_APIKEY", "GROQ_API_KEY": "NANOBOT_PROVIDERS_GROQ_APIKEY", "NANOBOT_MODEL": "NANOBOT_AGENTS_DEFAULTS_MODEL", "TELEGRAM_BOT_TOKEN": "NANOBOT_CHANNELS_TELEGRAM_TOKEN", "BRAVE_SEARCH_API_KEY": "NANOBOT_TOOLS_WEB_SEARCH_APIKEY"}`.
  - [x] Add the module docstring explaining this is the only file that needs updating when upstream config changes, and that it contains no logic — only data.

### Config Generator

- [x] **Create `scripts/config_generate.py`** — Create the file `scripts/config_generate.py` that imports `DEFAULTS`, `ENV_MAP`, `ARRAY_FIELDS`, `ALIASES` from `config_schema` and implements the full generation pipeline. The file must contain zero hardcoded config structure knowledge — all schema awareness comes from the imported data structures.
  - [x] **Deep-copy defaults** — `import copy; config = copy.deepcopy(DEFAULTS)` as the base config dict.
  - [x] **Read Docker secrets** — Scan `/run/secrets/` directory. For each file whose name starts with `NANOBOT_`, read its contents (strip trailing whitespace/newline) and set it as an environment variable only if that env var is not already set. This gives env vars precedence over secrets.
  - [x] **Resolve aliases** — Iterate over `ALIASES`. For each `(alias, canonical)` pair, if the alias is set in the environment and the canonical is not, set `os.environ[canonical] = os.environ[alias]`. If both are set, canonical wins (do nothing).
  - [x] **Parse NANOBOT_* env vars** — Iterate over all environment variables. For each starting with `NANOBOT_`, strip the `NANOBOT_` prefix and look up the suffix in `ENV_MAP`. If found, proceed to type inference and value setting. If not found, log a warning (`f"Unknown config key: NANOBOT_{suffix}, skipping"`) and skip.
  - [x] **Type inference** — For each matched value, apply this precedence: (1) if value is `"true"` or `"false"` (case-insensitive), convert to Python `bool`; (2) try `int(value)`, then `float(value)` — use the result if successful; (3) if value starts with `[` or `{`, parse with `json.loads()`; (4) if the suffix is in `ARRAY_FIELDS` and the value contains a comma, split on `,` and strip whitespace from each element to produce a `list[str]`; (5) else keep as string.
  - [x] **Set nested value** — For each `(suffix, value)` pair, retrieve the JSON path tuple from `ENV_MAP[suffix]`. Walk the config dict, creating intermediate `dict`s as needed, and set the final key to the inferred value.
  - [x] **Write config file** — Ensure `~/.nanobot/` directory exists (`os.makedirs`). Write the config dict to `~/.nanobot/config.json` using `json.dump` with `indent=2` for readability.
  - [x] **Logging** — Use `print()` to stderr or Python `logging` module. Log: number of env vars processed, any unknown keys skipped, any aliases resolved, the output file path.
  - [x] **Verify** — Run `NANOBOT_PROVIDERS_OPENROUTER_APIKEY=test123 NANOBOT_CHANNELS_TELEGRAM_ALLOWFROM="user1,user2" python scripts/config_generate.py` and confirm `~/.nanobot/config.json` contains `{"agents":{"defaults":{"model":"anthropic/claude-sonnet-4-5-20250514"}},"providers":{"openrouter":{"apiKey":"test123"}},"channels":{"telegram":{"allowFrom":["user1","user2"]}}}`.

## Nix Wrapper Scripts

- [ ] **Create `scripts/nix-install.sh`** — Create the file `scripts/nix-install.sh` (executable, `#!/usr/bin/env bash`, `set -euo pipefail`) that installs a Nix package with whitelist enforcement.
  - [ ] **Argument validation** — Accept exactly one argument: the package name. If no argument, print usage (`Usage: nix-install.sh <package>`) to stderr and exit 1.
  - [ ] **Whitelist check** — Read `NANOBOT_NIX_ALLOWED_PACKAGES` from the environment. If unset or empty, print `"Nix package installation is disabled (NANOBOT_NIX_ALLOWED_PACKAGES is not set)"` to stderr and exit 1. If set to `*`, allow any package. Otherwise, split the value on commas, trim whitespace from each element, and check if the requested package is in the list. If not, print `"Package '<name>' is not in the allowed list"` to stderr and exit 1.
  - [ ] **Already-installed check** — Run `nix-env -qaP "nixpkgs.$package" --installed 2>/dev/null` or check if the command the package provides is already on `PATH` via `command -v`. If already installed, print `"Package '<name>' is already installed"` and exit 0.
  - [ ] **Installation** — Run `nix-env -iA "nixpkgs.$package"`. If it fails, print `"Failed to install package '<name>'"` to stderr and exit 1. On success, print `"Package '<name>' installed successfully"`.
  - [ ] **Verify** — Run `chmod +x scripts/nix-install.sh` and confirm the script exits with the correct messages for: no args, empty whitelist, denied package, and wildcard whitelist (the actual install requires Nix, so logic-only testing is sufficient).

- [x] **Create `scripts/nix-search.sh`** — Create the file `scripts/nix-search.sh` (executable, `#!/usr/bin/env bash`, `set -euo pipefail`) that searches for available Nix packages.
  - [x] **Argument validation** — Accept exactly one argument: the search query. If no argument, print usage (`Usage: nix-search.sh <query>`) to stderr and exit 1.
  - [x] **Search execution** — Run `nix search nixpkgs "$query" 2>/dev/null` and pipe the output to stdout. If `nix search` is not available (older Nix), fall back to `nix-env -qaP "*$query*"`.
  - [x] **Verify** — Run `chmod +x scripts/nix-search.sh` and confirm the script prints usage when called with no args.

## Entrypoint Script

- [ ] **Create `scripts/entrypoint.sh`** — Create the file `scripts/entrypoint.sh` (executable, `#!/usr/bin/env bash`, `set -euo pipefail`) implementing the five-step startup sequence. Requires: Config Generation group and Nix Wrapper Scripts group to be complete.
  - [ ] **Step 1: Source Nix profile** — Check if `/root/.nix-profile/etc/profile.d/nix.sh` exists. If so, source it (`. /root/.nix-profile/etc/profile.d/nix.sh`). This adds Nix-installed packages to `PATH`. Do not fail if the file is missing (first run with empty `/nix` volume).
  - [ ] **Step 2: Nanobot onboard** — Check if the directory `~/.nanobot/workspace/` exists. If not, run `nanobot onboard` to bootstrap the workspace (creates config.json template, workspace dir, SOUL.md, TOOLS.md, AGENTS.md, etc.). This is idempotent — only runs on first boot.
  - [ ] **Step 3: Config generation** — Run `python3 /opt/nanobot-nix/scripts/config_generate.py` to produce/overwrite `~/.nanobot/config.json` from environment variables. This runs every startup so config changes via env vars take effect immediately.
  - [ ] **Step 4: Inject skills** — Create the target directory `~/.nanobot/workspace/skills/` if it doesn't exist. First, symlink all built-in skills: `for dir in /opt/nanobot-nix/skills/*/; do ln -sfn "$dir" ~/.nanobot/workspace/skills/$(basename "$dir"); done`. Then, overlay custom skills: `if [ -d /mnt/skills ]; then for dir in /mnt/skills/*/; do ln -sfn "$dir" ~/.nanobot/workspace/skills/$(basename "$dir"); done; fi`. Custom skills override built-in skills of the same name because symlinks are created with `-f` (force).
  - [ ] **Step 5: Exec nanobot** — `exec nanobot "$@"` — replace the shell process with nanobot, passing through all command-line arguments (e.g. `gateway`, `agent`).
  - [ ] **Verify** — Run `chmod +x scripts/entrypoint.sh` and confirm the script has correct syntax with `bash -n scripts/entrypoint.sh`.

## Skills

- [ ] **Create `skills/toolbox/SKILL.md`** — Create the file `skills/toolbox/SKILL.md` with YAML frontmatter containing `alwaysLoad: true`. The Markdown body must cover three sections:
  - [ ] **Container Environment Context** — Explain: running inside a read-only Docker container; writable paths are `/root/.nanobot` (workspace volume — sessions, memory, config), `/nix` (Nix package store volume — persists across restarts), and `/tmp` (tmpfs — cleared on restart); pre-installed tools: `git`, `jq`, `tmux`, `curl`, `gh` (GitHub CLI), `node` (Node.js 20), `python3`; base image is Debian-based.
  - [ ] **Nix Self-Provisioning Instructions** — Explain: before installing, check if the tool is already available with `which <tool>` or `command -v <tool>`; to install a package, run `/opt/nanobot-nix/scripts/nix-install.sh <package>`; to search for packages, run `/opt/nanobot-nix/scripts/nix-search.sh <query>`; include common package-to-command mappings (e.g. `ripgrep` provides `rg`, `fd` provides `fd`, `bat` provides `bat`); installation may be restricted by a whitelist — if denied, inform the user the package is not in the allowed list; installed packages persist across container restarts via the `/nix` volume.
  - [ ] **Nix Store Maintenance** — Explain: the `/nix` volume grows as packages are installed; to reclaim space, run `nix-collect-garbage -d` which removes unused packages and old generations; recommend running this periodically or when disk space is a concern.

## Dockerfile

- [ ] **Create `Dockerfile`** — Create the file `Dockerfile` at the repository root implementing the multi-stage build. Requires: Config Generation, Nix Wrapper Scripts, Entrypoint Script, and Skills groups to be complete.
  - [ ] **Build args** — Declare `ARG NANOBOT_REPO=https://github.com/HKUDS/nanobot.git` and `ARG NANOBOT_REF=main` at the top.
  - [ ] **Builder stage** — `FROM python:3.11-slim AS builder`. Install build dependencies: `apt-get update && apt-get install -y git curl nodejs npm && rm -rf /var/lib/apt/lists/*`. Install `uv`: `pip install uv`. Clone nanobot: `git clone --depth 1 --branch ${NANOBOT_REF} ${NANOBOT_REPO} /opt/nanobot`. Install nanobot: `cd /opt/nanobot && uv pip install --system -e .`. Build WhatsApp bridge: `cd /opt/nanobot/bridge && npm install && npm run build`.
  - [ ] **Runtime stage** — `FROM python:3.11-slim`. Install apt baseline packages: `apt-get update && apt-get install -y --no-install-recommends git jq tmux curl ca-certificates gnupg xz-utils && rm -rf /var/lib/apt/lists/*`. Install GitHub CLI (`gh`) via the official apt repository. Install Node.js 20 via NodeSource setup script or official binary tarball.
  - [ ] **Install Nix in runtime stage** — Set `ENV USER=root`. Install Nix in single-user mode: `curl -sL https://nixos.org/nix/install | sh -s -- --no-daemon`. Add `sandbox = false` to `/root/.config/nix/nix.conf`. Add Nix profile paths to `PATH` via `ENV PATH="/root/.nix-profile/bin:${PATH}"`. Add the `nixpkgs-unstable` channel: `nix-channel --add https://nixos.org/channels/nixpkgs-unstable nixpkgs && nix-channel --update`.
  - [ ] **Copy from builder** — Copy the nanobot installation from builder: `COPY --from=builder /opt/nanobot /opt/nanobot`. Copy Python site-packages: `COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages`. Copy nanobot entry point scripts: `COPY --from=builder /usr/local/bin/nanobot /usr/local/bin/nanobot`. Copy the bridge dist.
  - [ ] **Copy distro files** — `COPY scripts/ /opt/nanobot-nix/scripts/` and `COPY skills/ /opt/nanobot-nix/skills/`. Ensure scripts are executable: `RUN chmod +x /opt/nanobot-nix/scripts/*.sh`.
  - [ ] **Set ENTRYPOINT and CMD** — `ENTRYPOINT ["/opt/nanobot-nix/scripts/entrypoint.sh"]` and `CMD []`.
  - [ ] **Verify** — Run `docker build -t nanobot-nix:test .` and confirm it completes without errors (full verification requires Docker).

## Docker Compose

- [ ] **Create `docker-compose.yml`** — Create the file `docker-compose.yml` at the repository root defining the `gateway` and `cli` services. Requires: Dockerfile group to be complete (for image reference).
  - [ ] **Gateway service** — Service name `gateway`. Image: `ghcr.io/jinglemansweep/nanobot-nix:latest`. Command: `["gateway"]`. `restart: unless-stopped`. `read_only: true`. Ports: `["18790:18790"]`. `env_file: .env`. `tmpfs: ["/tmp"]`. Volumes: `nanobot-data:/root/.nanobot`, `nix-store:/nix`, `./skills:/mnt/skills:ro`. Add a healthcheck: `test: ["CMD", "curl", "-f", "http://localhost:18790"]`, `interval: 30s`, `timeout: 10s`, `retries: 3`, `start_period: 30s`.
  - [ ] **CLI service** — Service name `cli`. Image: `ghcr.io/jinglemansweep/nanobot-nix:latest`. Command: `["agent"]`. `profiles: [cli]`. `stdin_open: true`. `tty: true`. `read_only: true`. `env_file: .env`. `tmpfs: ["/tmp"]`. Volumes: same as gateway (`nanobot-data:/root/.nanobot`, `nix-store:/nix`, `./skills:/mnt/skills:ro`).
  - [ ] **Named volumes** — Declare top-level `volumes:` with `nanobot-data:` and `nix-store:` (both with default driver).
  - [ ] **Verify** — Run `docker compose config` and confirm the file is valid YAML and parses without errors.

## CI/CD

- [ ] **Create `.github/workflows/build.yml`** — Create the file `.github/workflows/build.yml` implementing the GitHub Actions CI/CD pipeline.
  - [ ] **Triggers** — `on: push: branches: [main]`, `on: push: tags: ["v*"]`, `on: schedule: cron: "0 4 * * 1"` (Monday 04:00 UTC), `on: workflow_dispatch: inputs: nanobot_ref: description: "Nanobot git ref to build" required: false default: "main"`.
  - [ ] **Permissions** — Set `permissions: contents: read` and `packages: write` at the workflow level.
  - [ ] **Registry login** — Job step using `docker/login-action@v3` with `registry: ghcr.io`, `username: ${{ github.actor }}`, `password: ${{ secrets.GITHUB_TOKEN }}`.
  - [ ] **Docker metadata** — Job step using `docker/metadata-action@v5` with `images: ghcr.io/jinglemansweep/nanobot-nix`. Tags: `type=ref,event=branch`, `type=ref,event=tag`, `type=sha`, `type=raw,value=latest,enable={{is_default_branch}}`, `type=raw,value={{date 'YYYYMMDD'}},enable=${{ github.event_name == 'schedule' }}`.
  - [ ] **Build and push** — Job step using `docker/build-push-action@v6` with `context: .`, `platforms: linux/amd64`, `push: true`, `tags: ${{ steps.meta.outputs.tags }}`, `labels: ${{ steps.meta.outputs.labels }}`, `build-args:` including `NANOBOT_REPO=https://github.com/HKUDS/nanobot.git` and `NANOBOT_REF=${{ github.event.inputs.nanobot_ref || 'main' }}`.
  - [ ] **Smoke test** — Add a step before the push step (or set `load: true` on a test build) that runs `docker run --rm <image> status` and asserts a zero exit code. This validates the image boots correctly.
  - [ ] **Verify** — Confirm the YAML is valid by running `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/build.yml'))"` (or equivalent linting).

## Documentation

- [ ] **Create `.env.example`** — Create the file `.env.example` at the repository root documenting all supported environment variables. Group by category with comments.
  - [ ] **Provider API keys** — Include: `NANOBOT_PROVIDERS_OPENROUTER_APIKEY=`, `NANOBOT_PROVIDERS_OPENROUTER_APIBASE=`, `NANOBOT_PROVIDERS_ANTHROPIC_APIKEY=`, `NANOBOT_PROVIDERS_ANTHROPIC_APIBASE=`, `NANOBOT_PROVIDERS_OPENAI_APIKEY=`, `NANOBOT_PROVIDERS_DEEPSEEK_APIKEY=`, `NANOBOT_PROVIDERS_GROQ_APIKEY=`, `NANOBOT_PROVIDERS_CUSTOM_APIKEY=`, `NANOBOT_PROVIDERS_CUSTOM_APIBASE=`. Add their aliases as comments next to each (e.g. `# Alias: OPENROUTER_API_KEY`).
  - [ ] **Agent config** — Include: `NANOBOT_AGENTS_DEFAULTS_MODEL=anthropic/claude-sonnet-4-5-20250514` (with comment showing alias `NANOBOT_MODEL`).
  - [ ] **Channel config** — Include all Telegram, Discord, Slack, WhatsApp vars. Note that `ALLOWFROM` vars accept comma-separated lists (e.g. `NANOBOT_CHANNELS_TELEGRAM_ALLOWFROM=user1,user2`).
  - [ ] **Tools config** — Include: `NANOBOT_TOOLS_WEB_SEARCH_APIKEY=` (alias: `BRAVE_SEARCH_API_KEY`), `NANOBOT_TOOLS_MCPSERVERS=` (note: JSON blob, e.g. `{"server1":{"command":"npx","args":[...]}}`).
  - [ ] **Nix config** — Include: `NANOBOT_NIX_ALLOWED_PACKAGES=` with comment explaining values (`*` = allow all, comma-separated list = allow only listed, empty = deny all).

- [ ] **Create `README.md`** — Create the file `README.md` at the repository root with project documentation.
  - [ ] **Header and overview** — Project name, one-sentence description ("Batteries-included Docker distribution of Nanobot with Nix self-provisioning"), badges (GHCR image, CI status).
  - [ ] **Quick start** — Show: `docker compose up -d` for gateway mode, `docker compose run --rm cli` for interactive CLI. Reference `.env.example` for configuration.
  - [ ] **Configuration reference** — Table of all `NANOBOT_*` env vars with description, type, default, and alias (if any). Explain the config generation pipeline and that `config.json` is regenerated on every container start.
  - [ ] **Custom skills** — Explain how to mount custom skills at `./skills:/mnt/skills:ro`, the symlink injection mechanism, and that custom skills override built-in skills of the same name.
  - [ ] **Nix self-provisioning** — Explain the `/nix` volume, the whitelist mechanism (`NANOBOT_NIX_ALLOWED_PACKAGES`), persistence behaviour, and garbage collection.
  - [ ] **Docker secrets** — Explain that config values can be provided via Docker secrets at `/run/secrets/NANOBOT_*` as an alternative to env vars, with env vars taking precedence.
  - [ ] **Building from source** — Show `docker build -t nanobot-nix .` with optional `--build-arg NANOBOT_REF=v0.1.4` to pin a specific version.
