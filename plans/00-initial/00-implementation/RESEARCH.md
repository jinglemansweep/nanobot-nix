# Research

> Source: `.agent/plans/01-initial/PROMPT.md`

## Nanobot (upstream project)
- **URL:** https://github.com/HKUDS/nanobot
- **Status:** Extremely active — 6 releases in Feb 2025 alone, 725+ commits, growing contributor base
- **Latest Version:** v0.1.4.post2 (Feb 24, 2025)
- **Compatibility:** Python >= 3.11, Node.js >= 20 (WhatsApp bridge only). PyPI package: `nanobot-ai`. Build system: Hatchling.
- **Key Findings:**
  - Ultra-lightweight AI assistant framework (~4k lines Python)
  - 15+ LLM providers via `litellm`, 9+ messaging channels
  - MCP server support added in v0.1.4
  - Config at `~/.nanobot/config.json`, validated by Pydantic, uses camelCase aliases in JSON
  - CLI commands: `onboard` (init workspace), `status` (system info), `gateway` (service mode, port 18790), `agent` (interactive CLI)
  - WhatsApp bridge is a separate Node.js/TypeScript process in `bridge/` dir using `@whiskeysockets/baileys`. Communicates with Python gateway over local WebSocket. Must be built separately (`npm install && npm run build`).
  - `nanobot onboard` creates `~/.nanobot/config.json`, workspace dir, and template files (SOUL.md, TOOLS.md, AGENTS.md, etc.)
  - Workspace structure: `~/.nanobot/workspace/` with skills, memory, sessions
  - Key Python deps: typer, litellm, pydantic, httpx, rich, loguru, mcp, croniter
  - Channel deps: python-telegram-bot, slack-sdk, websockets, lark-oapi, dingtalk-stream
  - Install from source: `git clone` + `pip install -e .` (or `uv pip install -e .`)
- **Concerns:**
  - Rapid release cadence means upstream config schema may change frequently — validates Decision 9 (isolating schema in a single data file)
  - The config JSON uses camelCase aliases (e.g. `apiKey`, `allowFrom`, `mcpServers`) — the prompt's ENV_MAP already accounts for this
  - WhatsApp bridge requires a separate build step (TypeScript compilation) and Node.js runtime
  - The `tools.mcpServers` path in the prompt's ENV_MAP uses camelCase `mcpServers`, consistent with upstream's JSON alias

## Nix Package Manager (in Docker / single-user mode)
- **URL:** https://nixos.org/
- **Status:** Actively maintained
- **Latest Version:** 2.33.3 (Feb 13, 2026)
- **Compatibility:** Runs in Docker with `--no-daemon` flag for single-user mode. Compatible with read-only containers when `/nix` is a writable volume.
- **Key Findings:**
  - Install with `curl -sL https://nixos.org/nix/install | sh -s -- --no-daemon` for single-user mode
  - `USER` env var must be set explicitly — Docker doesn't set it, and the Nix installer fails without it
  - `/nix` must be owned by the running user in single-user mode
  - `sandbox = false` required in containers (Docker seccomp conflicts with Nix sandboxing)
  - Key paths: `/nix/store/` (packages), `/nix/var/nix/db/` (SQLite DB), `/nix/var/nix/profiles/` (profiles)
  - Must mount entire `/nix` as volume (not just `/nix/store`) — DB must stay consistent with store
  - Profile sourcing: source `/root/.nix-profile/etc/profile.d/nix.sh` in entrypoint, or set `PATH` via Dockerfile `ENV`
  - `TMPDIR` must point to writable location (`/tmp` tmpfs)
  - Concurrent access to same `/nix` volume without daemon is unsafe — not a concern here since only one container writes at a time
- **Concerns:**
  - First run with empty `/nix` volume requires Nix to be installed into the volume — need to handle bootstrap vs subsequent runs
  - Nix installer downloads ~100MB+ which adds to image size; consider multi-stage approach or installing in builder and copying `/nix` to runtime

## GHCR (GitHub Container Registry)
- **URL:** https://ghcr.io
- **Status:** Production service by GitHub
- **Latest Version:** N/A (managed service)
- **Compatibility:** Standard OCI registry, works with `docker/build-push-action` and `docker/login-action` in GitHub Actions
- **Key Findings:**
  - Authenticate via `GITHUB_TOKEN` in Actions workflows
  - Image path: `ghcr.io/<owner>/<repo>` — prompt specifies `ghcr.io/jinglemansweep/nanobot-nix`
  - Supports multi-arch manifests via `docker/build-push-action` with QEMU
- **Concerns:** None — well-established workflow

## uv (Python package installer)
- **URL:** https://github.com/astral-sh/uv
- **Status:** Actively maintained
- **Latest Version:** Current stable (fast-moving project)
- **Compatibility:** Drop-in replacement for pip, used in builder stage for `uv pip install -e .`
- **Key Findings:**
  - Significantly faster than pip for package installation
  - Prompt specifies using `uv pip install -e .` in builder stage
  - Available via pip, pipx, or standalone installer
- **Concerns:** None — straightforward usage in builder stage
