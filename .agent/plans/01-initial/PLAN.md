# Implementation Plan

> Source: `.agent/plans/01-initial/PROMPT.md`

## Overview

A batteries-included Docker distribution of Nanobot (`ghcr.io/jinglemansweep/nanobot-nix`) that packages the upstream Nanobot AI assistant with baseline tooling, Nix for runtime self-provisioning, environment-driven config generation, and a hot-reloadable skills system. The image is built and published via GitHub Actions CI/CD for `linux/amd64` with weekly upstream tracking.

## Architecture & Approach

The image uses a **multi-stage Docker build**: a builder stage clones Nanobot at a configurable ref, installs it with `uv`, and compiles the WhatsApp bridge; a runtime stage assembles a slim image with apt baseline tools, Node.js 20, single-user Nix, and the distro's scripts and skills.

The container runs **read-only** with three writable mounts: `/nix` (Nix store volume for agent-installed packages), `/root/.nanobot` (workspace, config, sessions, memory), and `/tmp` (tmpfs). This gives the agent a persistent, mutable workspace while keeping the base image immutable.

**Config generation** follows a strict two-file separation of concerns: `config_schema.py` holds all schema knowledge as pure declarative data (env var mappings, aliases, array fields, defaults), while `config_generate.py` contains all logic (env parsing, type inference, JSON writing) but zero schema awareness. This means upstream config changes only ever touch one file.

**Skills** are injected at startup via symlinks. Built-in skills are baked into the image at `/opt/nanobot-nix/skills/`, user custom skills are bind-mounted at `/mnt/skills/:ro`. The entrypoint symlinks both into the workspace skills directory, with custom skills taking precedence. This gives hot-reload behaviour — filesystem changes are immediately visible through the symlinks.

**Nix** is installed in single-user/daemon-less mode. Wrapper scripts (`nix-install.sh`, `nix-search.sh`) provide a controlled interface for the agent to self-provision tools at runtime, gated by an env-var whitelist. Packages persist across container restarts via the `/nix` volume.

**CI/CD** uses GitHub Actions with `docker/build-push-action` for `linux/amd64` builds, pushing to GHCR. Triggers include push-to-main, tags, weekly schedule, and manual dispatch with a configurable `nanobot_ref`. arm64 support is deferred to avoid QEMU emulation flakiness in CI.

## Components

### Multi-Stage Dockerfile

**Purpose:** Produce a minimal, reproducible Docker image containing Nanobot, its WhatsApp bridge, baseline tools, Nix, and the distro's scripts/skills.

**Inputs:** Build args `NANOBOT_REPO` (default `https://github.com/HKUDS/nanobot.git`) and `NANOBOT_REF` (default `main`).

**Outputs:** A `linux/amd64` OCI image tagged and pushed to `ghcr.io/jinglemansweep/nanobot-nix`.

**Notes:**
- Builder stage: Python 3.11+ base, clones nanobot at `NANOBOT_REF`, runs `uv pip install -e .`, then builds the WhatsApp bridge (`cd bridge && npm install && npm run build`).
- Runtime stage: slim Debian-based image. Installs apt baseline (`git, jq, tmux, curl, ca-certificates, gnupg, xz-utils, gh`), Node.js 20 (via NodeSource or official binary), and Nix directly in the runtime stage in single-user mode (`--no-daemon`, `sandbox = false`). Uses `nixpkgs-unstable` channel.
- Copies nanobot installation, bridge dist, and distro files (`scripts/`, `skills/`) from builder.
- Sets `USER` env var explicitly for Nix compatibility.
- Nix profile paths added to `PATH` via `ENV` directive so they're available in entrypoint without sourcing.
- Entrypoint set to `scripts/entrypoint.sh`, default command is empty (user provides `gateway`, `agent`, etc.).
- WhatsApp bridge is built but not auto-started — users run it separately if needed.

### Config Schema (`config_schema.py`)

**Purpose:** Single source of truth for the mapping between flat `NANOBOT_*` environment variables and Nanobot's nested JSON config structure. Contains no logic — only four declarative data structures.

**Inputs:** None (pure data).

**Outputs:** Exports `DEFAULTS`, `ENV_MAP`, `ARRAY_FIELDS`, `ALIASES` for use by the generator.

**Notes:**
- `DEFAULTS` provides the base config structure (e.g. default model).
- `ENV_MAP` maps env var suffixes to JSON path tuples (e.g. `"PROVIDERS_OPENROUTER_APIKEY" → ("providers", "openrouter", "apiKey")`).
- `ARRAY_FIELDS` identifies keys whose comma-separated values should become JSON arrays.
- `ALIASES` maps common env var names (e.g. `OPENROUTER_API_KEY`) to their canonical `NANOBOT_*` equivalents.
- The prompt provides the complete content of this file — it should be implemented as specified.

### Config Generator (`config_generate.py`)

**Purpose:** Read environment variables, consult the schema, and produce `~/.nanobot/config.json`. Completely schema-agnostic — all config structure knowledge comes from importing `config_schema.py`.

**Inputs:** Environment variables, imported schema data structures.

**Outputs:** `~/.nanobot/config.json`.

**Notes:**
- Deep-copies `DEFAULTS` as base config.
- Checks `/run/secrets/` for Docker secrets: for each file named `NANOBOT_*`, reads its contents and treats it as the env var value. Env vars take precedence over secrets if both are set.
- Resolves aliases first (canonical wins if both set).
- Scans all `NANOBOT_*` env vars, strips prefix, looks up in `ENV_MAP`.
- Unknown keys produce a warning log but are skipped.
- Type inference order: bool (`true`/`false`), number (int/float), JSON literal (starts with `[` or `{`), array (key in `ARRAY_FIELDS` and value contains commas → split+trim), else string.
- Sets values at nested JSON paths, creating intermediate dicts as needed.
- Writes formatted JSON to `~/.nanobot/config.json`.

### Entrypoint Script (`entrypoint.sh`)

**Purpose:** Orchestrate container startup: source Nix, initialise workspace, generate config, inject skills, then exec nanobot.

**Inputs:** Environment variables, mounted volumes.

**Outputs:** Ready-to-run nanobot process.

**Notes:**
- Step 1: Source Nix profile (`/root/.nix-profile/etc/profile.d/nix.sh`) if it exists.
- Step 2: Run `nanobot onboard` if `~/.nanobot/workspace/` directory doesn't exist yet (first-run bootstrap).
- Step 3: Run `config_generate.py` to produce/overwrite `~/.nanobot/config.json` from env vars.
- Step 4: Symlink built-in skills from `/opt/nanobot-nix/skills/*` into `~/.nanobot/workspace/skills/`, then overlay custom skills from `/mnt/skills/*` (custom overrides built-in on name collision).
- Step 5: `exec nanobot "$@"` — hands off to nanobot with whatever command the user provided.

### Nix Install Wrapper (`nix-install.sh`)

**Purpose:** Provide a controlled, whitelist-gated interface for the agent to install Nix packages at runtime.

**Inputs:** Package name argument, `NANOBOT_NIX_ALLOWED_PACKAGES` env var.

**Outputs:** Installed package available on `PATH` via Nix profile.

**Notes:**
- Whitelist behaviour: `*` allows any package, comma-separated list allows only listed packages, empty/unset denies all.
- Should check if package is already installed before attempting install.
- Uses `nix-env -iA nixpkgs.<package>` or `nix profile install nixpkgs#<package>`.
- Exits with clear error messages for denied or failed installs.

### Nix Search Wrapper (`nix-search.sh`)

**Purpose:** Let the agent search for available Nix packages by query.

**Inputs:** Search query argument.

**Outputs:** List of matching package names to stdout.

**Notes:**
- Uses `nix search nixpkgs <query>` or `nix-env -qaP <query>`.
- Should produce concise, parseable output suitable for the agent to read.

### Toolbox Skill (`skills/toolbox/SKILL.md`)

**Purpose:** A single always-loaded skill that informs the agent about its container environment and how to self-provision tools via Nix.

**Inputs:** None (static Markdown content loaded by Nanobot's skill system).

**Outputs:** Contextual knowledge available to the agent.

**Notes:**
- Covers three areas: container environment context (writable paths, pre-installed tools, read-only constraint), Nix self-provisioning instructions (how to install, search, check before installing, whitelist behaviour, persistence), and Nix store maintenance (how and when to run `nix-collect-garbage -d`).
- Loaded with `alwaysLoad: true` in the skill's frontmatter/metadata.
- Must reference the actual script paths: `/opt/nanobot-nix/scripts/nix-install.sh` and `/opt/nanobot-nix/scripts/nix-search.sh`.

### GitHub Actions Workflow (`build.yml`)

**Purpose:** Automate building, testing, and publishing the Docker image to GHCR.

**Inputs:** Triggers (push to main, tags, weekly schedule Mon 04:00 UTC, manual dispatch with `nanobot_ref` input).

**Outputs:** Published image at `ghcr.io/jinglemansweep/nanobot-nix` with appropriate tags.

**Notes:**
- Build args: `NANOBOT_REPO`, `NANOBOT_REF` (from manual dispatch input or default `main`).
- Single-arch via `docker/build-push-action` with `platforms: linux/amd64`. arm64 deferred.
- Tags: `latest`, semver (on tag push), git sha, `YYYYMMDD` for scheduled builds.
- Smoke test: run `nanobot status` in the built image before pushing (validates the image works).
- Uses `docker/login-action` with `GITHUB_TOKEN` for GHCR auth.
- Uses `docker/metadata-action` for tag generation.

### Docker Compose (`docker-compose.yml`)

**Purpose:** Provide ready-to-use service definitions for running nanobot-nix locally.

**Inputs:** `.env` file, optional `./skills` bind mount.

**Outputs:** Running `gateway` and optional `cli` services.

**Notes:**
- Two services: `gateway` (always-on, port 18790) and `cli` (on-demand via `docker compose run cli`).
- Both use `read_only: true` with writable volumes for `/root/.nanobot`, `/nix`, and `/tmp` (tmpfs).
- Custom skills mounted at `./skills:/mnt/skills:ro`.
- The `cli` service uses `profiles: [cli]` so it doesn't start with `docker compose up`.
- The `gateway` service includes a healthcheck hitting `http://localhost:18790` (or appropriate endpoint) to support `depends_on` with `condition: service_healthy`.

### Environment Example (`.env.example`)

**Purpose:** Document all supported environment variables with descriptions and example values.

**Inputs:** All keys from `ENV_MAP` and `ALIASES` in `config_schema.py`.

**Outputs:** Template `.env` file for user reference.

**Notes:**
- Should include every `NANOBOT_*` variable and its alias (if any), grouped by category.
- Comments explaining each variable's purpose and format.
- Include `NANOBOT_NIX_ALLOWED_PACKAGES` for the Nix whitelist.

### Gitignore (`.gitignore`)

**Purpose:** Prevent committing generated files, secrets, and build artifacts.

**Inputs:** None.

**Outputs:** `.gitignore` rules.

**Notes:**
- Should cover: `.env`, `__pycache__/`, `*.pyc`, `node_modules/`, build artifacts, editor files.

### README (`README.md`)

**Purpose:** Project documentation covering what nanobot-nix is, how to use it, and how to configure it.

**Inputs:** All project knowledge.

**Outputs:** User-facing documentation.

**Notes:**
- Quick start, configuration reference, custom skills guide, Nix provisioning explanation, contributing notes.

## File Manifest

| File | Action | Purpose |
|------|--------|---------|
| `Dockerfile` | Create | Multi-stage build: builder (nanobot + bridge) → runtime (slim + apt + Node.js + Nix) |
| `docker-compose.yml` | Create | Gateway and CLI service definitions with volumes |
| `.github/workflows/build.yml` | Create | CI/CD: amd64 build, smoke test, push to GHCR |
| `scripts/entrypoint.sh` | Create | Startup orchestration: Nix, onboard, config, skills, exec |
| `scripts/config_schema.py` | Create | Declarative config mapping (ENV_MAP, ALIASES, ARRAY_FIELDS, DEFAULTS) |
| `scripts/config_generate.py` | Create | Schema-agnostic env→JSON config generator |
| `scripts/nix-install.sh` | Create | Whitelist-gated Nix package installer |
| `scripts/nix-search.sh` | Create | Nix package search helper |
| `skills/toolbox/SKILL.md` | Create | Built-in skill: container context + Nix self-provisioning instructions |
| `.env.example` | Create | Documented template of all supported env vars |
| `.gitignore` | Create | Ignore rules for secrets, build artifacts, caches |
| `README.md` | Create | Project documentation |
