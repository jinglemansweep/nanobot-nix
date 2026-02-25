# Task List

> Source: `.agent/plans/03-testing-01/PLAN.md`

## Dockerfile — Nix Installation Block

### Replace Nix Installer

- [x] **Remove the `ENV USER=root` line** — Delete line 51 (`ENV USER=root`) from `Dockerfile`. The DeterminateSystems installer handles root natively and does not need this variable.

- [x] **Replace the Nix installation RUN block** — Replace lines 52–54 of `Dockerfile` (the `RUN curl -sL https://nixos.org/nix/install | sh -s -- --no-daemon && ...` block) with the DeterminateSystems installer:
  ```dockerfile
  RUN curl --proto '=https' --tlsv1.2 -sSf -L \
      https://install.determinate.systems/nix | sh -s -- install linux \
      --extra-conf "sandbox = false" --init none --no-confirm
  ```
  This installs Nix with: no systemd init (`--init none`), non-interactive mode (`--no-confirm`), and disabled sandboxing for container compatibility (`--extra-conf "sandbox = false"`). No version pinning — always use the latest installer.

- [x] **Update the PATH environment variable** — Replace line 55 of `Dockerfile` (`ENV PATH="/root/.nix-profile/bin:${PATH}"`) with:
  ```dockerfile
  ENV PATH="${PATH}:/nix/var/nix/profiles/default/bin"
  ```
  The DeterminateSystems installer places Nix binaries at `/nix/var/nix/profiles/default/bin` instead of `/root/.nix-profile/bin`.

### Remove Channel Management

- [x] **Remove the nix-channel RUN block** — Delete lines 56–57 of `Dockerfile` (the `RUN nix-channel --add ... && nix-channel --update` block). Flakes-based commands use `nixpkgs#<pkg>` registry references directly, so channel management is no longer needed. The DeterminateSystems installer configures the Nix registry by default.

### Update Dockerfile Comment

- [x] **Update the section comment** — Replace the comment on line 50 (`# Install Nix in single-user mode`) with `# Install Nix via DeterminateSystems installer` to accurately reflect the new approach.

## Entrypoint — Nix Profile Sourcing

- [x] **Update the Nix profile source path in entrypoint** — In `scripts/entrypoint.sh`, replace lines 5–8:
  ```bash
  if [ -f /root/.nix-profile/etc/profile.d/nix.sh ]; then
    # shellcheck source=/dev/null
    . /root/.nix-profile/etc/profile.d/nix.sh
  fi
  ```
  with:
  ```bash
  if [ -f /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh ]; then
    # shellcheck source=/dev/null
    . /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
  fi
  ```
  The DeterminateSystems installer places the profile script at `/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh`. The `if [ -f ... ]` guard is kept for safety. This ensures Nix env vars (`NIX_PATH`, `NIX_PROFILES`) are set correctly for flakes-based commands at runtime.

## Runtime Scripts — Flakes Migration

### nix-install.sh

- [x] **Replace the already-installed check** — In `scripts/nix-install.sh`, replace lines 36–39 (the `nix-env -qaP` already-installed check):
  ```bash
  if nix-env -qaP "nixpkgs.$package" --installed 2>/dev/null | grep -q .; then
      echo "Package '$package' is already installed"
      exit 0
  fi
  ```
  with a `nix profile list` check:
  ```bash
  if nix profile list 2>/dev/null | grep -q "nixpkgs#$package"; then
      echo "Package '$package' is already installed"
      exit 0
  fi
  ```
  The `nix profile list` command shows installed flake references; grepping for `nixpkgs#<package>` detects whether the package is already installed.

- [x] **Replace the installation command** — In `scripts/nix-install.sh`, replace lines 42–45 (the `nix-env -iA` installation block):
  ```bash
  if ! nix-env -iA "nixpkgs.$package"; then
      echo "Failed to install package '$package'" >&2
      exit 1
  fi
  ```
  with:
  ```bash
  if ! nix profile install "nixpkgs#$package"; then
      echo "Failed to install package '$package'" >&2
      exit 1
  fi
  ```
  The `nix profile install nixpkgs#<pkg>` command uses flake references to install packages from the nixpkgs registry, replacing the legacy `nix-env -iA nixpkgs.<pkg>` approach.

### nix-search.sh

- [x] **Simplify the search command** — In `scripts/nix-search.sh`, replace lines 12–17 (the dual-path search logic):
  ```bash
  # Search execution — try `nix search` first, fall back to `nix-env` for older Nix
  if command -v nix &>/dev/null && nix search nixpkgs "$query" 2>/dev/null; then
      :
  else
      nix-env -qaP "*${query}*"
  fi
  ```
  with:
  ```bash
  # Search execution
  nix search nixpkgs "$query"
  ```
  The DeterminateSystems installer enables `nix-command` and `flakes` experimental features by default, so `nix search nixpkgs <query>` is guaranteed to work. The `nix-env` fallback is no longer needed. The script's `set -euo pipefail` at line 2 already handles errors — if `nix search` fails, the script exits non-zero automatically.

## Validation

- [x] **Build the Docker image locally** — Run `docker build -t nanobot-nix:test .` from the project root and verify the build completes without errors. The DeterminateSystems installer should install Nix successfully as root, and the PATH should be set correctly. No channel update step should appear in the build output.

- [x] **Smoke-test Nix availability** — Run `docker run --rm nanobot-nix:test nix --version` and verify it outputs a Nix version string (e.g. `nix (Nix) 2.x.x`). This confirms the PATH and Nix installation are correct.

- [x] **Smoke-test nix profile install** — Run `docker run --rm nanobot-nix:test nix profile install nixpkgs#hello && hello` and verify it installs the `hello` package and prints `Hello, world!`. This confirms flakes-based installation works in the container environment.

- [ ] **Smoke-test nix search** — Run `docker run --rm nanobot-nix:test nix search nixpkgs hello` and verify it returns search results including the `hello` package. This confirms flakes-based search works without channel configuration.

- [ ] **Run existing tests and pre-commit** — Run `pre-commit run --all-files` and `pytest` to ensure no existing tests or linting rules are broken by the changes. Fix any failures before proceeding.
