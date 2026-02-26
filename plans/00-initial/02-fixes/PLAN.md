# Implementation Plan

> Source: `.agent/plans/03-testing-01/PROMPT.md`

## Overview

The Docker image build fails because the official Nix install script (`nixos.org/nix/install`) does not support running as root and attempts to use `sudo`, which is not available in the slim base image. This plan replaces the Nix installation method with the DeterminateSystems installer, which has first-class Docker and root support, and adjusts the entrypoint and PATH configuration to match the new installation layout. Additionally, since the DeterminateSystems installer enables flakes by default, the runtime scripts are migrated from legacy `nix-env`/`nix-channel` to flakes-based commands (`nix profile install`, `nix search`), eliminating channel management entirely. The installer is always used at its latest version (no version pinning build arg).

## Architecture & Approach

The fix targets the Nix installation block in the runtime stage of the Dockerfile (lines 50-57). The current approach pipes the official Nix install script through `sh` with `--no-daemon`, which fails for root-in-Docker. The replacement uses the DeterminateSystems installer (`install.determinate.systems/nix`) with Docker-specific flags: `--init none` (no systemd), `--no-confirm` (non-interactive), and `--extra-conf "sandbox = false"` (container compatibility).

The DeterminateSystems installer places Nix binaries at `/nix/var/nix/profiles/default/bin` rather than `/root/.nix-profile/bin`, so all PATH references and profile-sourcing in the entrypoint must be updated accordingly. Since flakes are enabled by default, the runtime scripts (`nix-install.sh`, `nix-search.sh`) are migrated from `nix-env -iA nixpkgs.<pkg>` to `nix profile install nixpkgs#<pkg>` and from channel-based search to `nix search nixpkgs <query>`. This eliminates the need for `nix-channel --add` and `nix-channel --update` in the Dockerfile.
## Components

### Dockerfile Nix Installation Block

**Purpose:** Install Nix into the runtime image so containers can dynamically install packages via `nix profile install`.

**Inputs:** Network access to `install.determinate.systems/nix` during build.

**Outputs:** A working Nix installation at `/nix/var/nix/profiles/default/` with flakes enabled.

**Notes:**
- The `ENV USER=root` line (line 51) can be removed — the DeterminateSystems installer handles root natively.
- The `mkdir -p /root/.config/nix` and `echo "sandbox = false"` lines are replaced by the `--extra-conf` flag.
- The PATH must change from `/root/.nix-profile/bin` to `/nix/var/nix/profiles/default/bin`.
- The `nix-channel --add` and `nix-channel --update` commands are no longer needed — flakes-based commands use `nixpkgs#<pkg>` registry references directly.
- No version pinning build arg — always use the latest installer.

### Entrypoint Nix Profile Sourcing

**Purpose:** Ensure Nix binaries are available in the container's runtime environment when the entrypoint script runs.

**Inputs:** The Nix profile script installed by the DeterminateSystems installer.

**Outputs:** Nix binaries on the PATH for subsequent entrypoint steps and the main nanobot process.

**Notes:**
- The current entrypoint sources `/root/.nix-profile/etc/profile.d/nix.sh`. Update to source `/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh` instead. Keep the `if [ -f ... ]` guard for safety.
- Profile sourcing is preferred over relying solely on `ENV PATH` — it ensures Nix env vars (like `NIX_PATH`, `NIX_PROFILES`) are set correctly for flakes-based commands.

### Docker Compose Volume Compatibility

**Purpose:** Ensure the Nix store volume mount continues to work with the new installation layout.

**Inputs:** `nix-store:/nix` volume mount in `docker-compose.yml`.

**Outputs:** Persistent Nix store across container restarts.

**Notes:**
- The volume mount is at `/nix`, which is the same root for both the old and new installer. No changes needed to `docker-compose.yml`.
- On first boot with an empty volume, the entrypoint will have a working Nix from the image layer. On subsequent boots, the volume overlays `/nix` with the persisted store, which should be compatible.

### Runtime Scripts Flakes Migration

**Purpose:** Migrate `nix-install.sh` and `nix-search.sh` from legacy `nix-env`/`nix-channel` commands to flakes-based equivalents.

**Inputs:** Existing script logic for package installation and search.

**Outputs:** Scripts that use `nix profile install nixpkgs#<pkg>` and `nix search nixpkgs <query>` instead of `nix-env -iA nixpkgs.<pkg>` and channel-based search.

**Notes:**
- `nix-install.sh`: Replace `nix-env -iA nixpkgs.<pkg>` with `nix profile install nixpkgs#<pkg>`. The `nixpkgs` flake reference resolves via the Nix registry (which the DeterminateSystems installer configures by default).
- `nix-search.sh`: Replace channel-based search with `nix search nixpkgs <query>`. Output format may differ — ensure the script parses the new output correctly or uses `--json` for structured output.
- Both scripts should use `--experimental-features 'nix-command flakes'` flags if not already enabled in `nix.conf`. The DeterminateSystems installer enables these by default, but being explicit is defensive.
- Test that `nix profile install` and `nix search` work correctly in the container environment.

### CI Workflow Validation

**Purpose:** Ensure the `build.yml` GitHub Actions workflow can build and smoke-test the fixed image.

**Inputs:** The updated Dockerfile.

**Outputs:** A successful CI build with passing smoke test (`docker run --rm nanobot-nix:smoke-test status`).

**Notes:**
- No changes to the workflow file itself are needed — the build context, build args, and smoke test command remain the same.
- The smoke test (`nanobot status`) validates that nanobot is installed and runnable, not that Nix works. Consider whether an additional smoke test for Nix (e.g., `nix --version`) would be valuable.

## File Manifest

| File | Action | Purpose |
|------|--------|---------|
| `Dockerfile` | Modify | Replace Nix installation block with DeterminateSystems installer; update PATH; remove channel setup |
| `scripts/entrypoint.sh` | Modify | Update Nix profile source path to `/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh` |
| `scripts/nix-install.sh` | Modify | Migrate from `nix-env -iA` to `nix profile install nixpkgs#<pkg>` |
| `scripts/nix-search.sh` | Modify | Migrate from channel-based search to `nix search nixpkgs <query>` |
