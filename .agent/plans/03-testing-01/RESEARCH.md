# Research

> Source: `.agent/plans/03-testing-01/PROMPT.md`

## Official Nix Install Script (`nixos.org/nix/install`)

- **URL:** https://nixos.org/nix/install
- **Status:** Actively maintained (part of official Nix distribution)
- **Latest Version:** Nix 2.33.3 (referenced in the error log)
- **Compatibility:** Does NOT support running as root — the script explicitly rejects root execution and attempts to use `sudo` to create `/nix`, which fails in Docker containers where `sudo` is not installed.
- **Key Findings:**
  - The script is designed for desktop/server installations, not containers.
  - It assumes `sudo` is available when run as root.
  - The `--no-daemon` flag selects single-user mode but does not bypass the root check.
  - The error message `sudo: not found` confirms the root cause: the script tries `mkdir -m 0755 /nix && chown root /nix` via `sudo`, but `sudo` is not present in the slim base image.
- **Concerns:** This installer is fundamentally unsuitable for root-in-Docker without workarounds.

## Official NixOS Docker Image (`NixOS/docker`)

- **URL:** https://github.com/NixOS/docker/blob/master/Dockerfile
- **Status:** Archived (December 2021), read-only
- **Latest Version:** Nix 2.3.15 (pinned in the Dockerfile)
- **Compatibility:** Based on Alpine, uses a manual tarball download approach
- **Key Findings:**
  - Pre-creates `/nix` with `mkdir -m 0755 /nix` before running the installer.
  - Downloads a specific Nix version tarball, extracts it, and runs the install script directly from the extracted directory with `USER=root sh install`.
  - Creates `nixbld` group and 30 build users (for multi-user features).
  - Sets up `/etc/nix/nix.conf` with `sandbox = false` before installation.
  - Runs garbage collection and store verification after install.
- **Concerns:** Archived and pinned to an old Nix version. Pattern is valid but requires manual maintenance of version numbers.

## DeterminateSystems Nix Installer

- **URL:** https://github.com/DeterminateSystems/nix-installer
- **Status:** Actively maintained (7+ million installs)
- **Latest Version:** Versioned via GitHub releases (tags like `v0.6.0+`)
- **Compatibility:** First-class Docker support with documented Dockerfile examples
- **Key Findings:**
  - Explicit Docker support with `--init none` flag (no systemd required).
  - Supports root installation natively.
  - `--no-confirm` flag for non-interactive use in Dockerfiles.
  - `--extra-conf "sandbox = false"` for container compatibility.
  - Nix binaries installed to `/nix/var/nix/profiles/default/bin`.
  - Documented Dockerfile example:
    ```dockerfile
    RUN curl --proto '=https' --tlsv1.2 -sSf -L \
      https://install.determinate.systems/nix | sh -s -- install linux \
      --extra-conf "sandbox = false" --init none --no-confirm
    ENV PATH="${PATH}:/nix/var/nix/profiles/default/bin"
    ```
  - When using `--init none`, only root or users who can elevate to root can run Nix.
- **Concerns:** Third-party installer (not official NixOS), but NixOS has forked it as `NixOS/nix-installer` indicating community acceptance.

## NixOS/nix-installer (Upstream Fork)

- **URL:** https://github.com/NixOS/nix-installer
- **Status:** Actively maintained (official NixOS fork of DeterminateSystems installer)
- **Latest Version:** Tracks DeterminateSystems releases
- **Compatibility:** Same Docker support as DeterminateSystems variant
- **Key Findings:**
  - Official NixOS blessing of the DeterminateSystems installer approach.
  - Same flags and behaviour as the DeterminateSystems version.
  - Provides an alternative installation URL if vendor lock-in is a concern.
- **Concerns:** Newer fork, may lag behind DeterminateSystems releases.

## Mitchell Hashimoto's "Nix with Dockerfiles" Article

- **URL:** https://mitchellh.com/writing/nix-with-dockerfiles
- **Status:** Published reference article
- **Key Findings:**
  - Recommends using `nixos/nix:latest` as a build stage base instead of installing Nix into an arbitrary image.
  - This approach is not suitable for nanobot-nix because Nix must be available at runtime (for dynamic package installation), not just at build time.
- **Concerns:** Not applicable to our use case since we need Nix in the runtime image.
