---
alwaysLoad: true
---

# Toolbox

## Container Environment Context

You are running inside a **read-only Docker container** based on Debian. The filesystem is read-only except for the following writable paths:

- **`/root/.nanobot`** — Workspace volume. Contains sessions, memory, config (`config.json`), and all workspace data. Persists across container restarts.
- **`/nix`** — Nix package store volume. Contains all Nix-installed packages and generations. Persists across container restarts.
- **`/tmp`** — Temporary filesystem (tmpfs). Cleared on every container restart. Use for throwaway files only.

The following tools are **pre-installed** and available on `PATH`:

- `git` — Version control
- `jq` — JSON processor
- `tmux` — Terminal multiplexer
- `curl` — HTTP client
- `gh` — GitHub CLI
- `node` — Node.js 20
- `python3` — Python 3.11

## Nix Self-Provisioning Instructions

You can install additional tools on-demand using Nix. Installed packages persist across container restarts via the `/nix` volume.

**Before installing**, always check if the tool is already available:

```bash
which <tool> || command -v <tool>
```

**To search for packages:**

```bash
/opt/nanobot-nix/scripts/nix-search.sh <query>
```

**To install a package:**

```bash
/opt/nanobot-nix/scripts/nix-install.sh <package>
```

Common package-to-command mappings:

| Package    | Command |
|------------|---------|
| `ripgrep`  | `rg`    |
| `fd`       | `fd`    |
| `bat`      | `bat`   |
| `eza`      | `eza`   |
| `delta`    | `delta` |
| `htop`     | `htop`  |
| `tree`     | `tree`  |

Installation may be restricted by a whitelist. If a package is denied, it means the package is not in the allowed list configured by the user. Inform the user that the requested package is not permitted.

## Nix Store Maintenance

The `/nix` volume grows as packages are installed. To reclaim disk space, run:

```bash
nix-collect-garbage -d
```

This removes unused packages and old Nix generations. Run this periodically or when disk space is a concern.
