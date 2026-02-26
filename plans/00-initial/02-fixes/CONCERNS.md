# Concerns

> Source: `.agent/plans/03-testing-01/PROMPT.md`

## Open Questions

- [RESOLVED] **Nix profile script location:** The exact path to the Nix profile script under the DeterminateSystems installer needs to be confirmed. It is likely `/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh` but could vary by version. The entrypoint should handle the case where the file doesn't exist (which it already does via the `if [ -f ... ]` guard). → **Decision:** Update the entrypoint to source `/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh`. Keep the `if [ -f ... ]` guard for safety.
- [RESOLVED] **Channel setup in same layer:** After the DeterminateSystems installer runs, `nix-channel` may not be on the PATH within the same `RUN` instruction unless the profile is explicitly sourced. The Dockerfile may need to either chain commands with profile sourcing or use a separate `RUN` with the `ENV PATH` already set. → **Decision:** Source the profile inline in the same RUN instruction: install Nix, then `. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh && nix-channel --add ... && nix-channel --update`.

## Potential Blockers

- [RESOLVED] **DeterminateSystems installer availability:** The installation URL (`install.determinate.systems/nix`) is a third-party service. If it goes down during a Docker build, the build will fail. This is the same class of risk as the current approach (which fetches from `nixos.org`). The `NixOS/nix-installer` fork could serve as a fallback. → **Decision:** Use the DeterminateSystems URL directly. Same risk class as current approach; no fallback logic needed.

## Risks

- [RESOLVED] **Installer behaviour changes:** The DeterminateSystems installer is versioned but the install URL fetches the latest by default. A breaking change in a new release could cause future build failures. Pinning to a specific version (e.g., `https://install.determinate.systems/nix/tag/v0.31.1`) would mitigate this but adds maintenance burden. → **Decision:** Don't pin the installer version. Use latest for simplicity and automatic security fixes. Breaking changes are rare.
- [RESOLVED] **Nix store volume migration:** Existing deployments with a populated `nix-store:/nix` volume may have store contents from the old installer. The DeterminateSystems installer uses the same `/nix/store` layout so this should be compatible, but has not been verified. → **Decision:** Accept the risk. The `/nix/store` layout is a Nix standard, not installer-specific. Users can delete and recreate the volume if issues arise.

## Future Considerations

- [RESOLVED] **Nix flakes migration:** The DeterminateSystems installer enables flakes by default. The current `nix-install.sh` and `nix-search.sh` scripts use the legacy `nix-env` / `nix-channel` interface. A future improvement could migrate these scripts to use `nix profile install nixpkgs#<pkg>` and `nix search nixpkgs <query>`, eliminating the need for channel management entirely. → **Decision:** Include flakes migration in this plan. Migrate scripts to use `nix profile install` and `nix search`, eliminating channel management.
- [RESOLVED] **Multi-platform builds:** The current CI builds for `linux/amd64` only. The DeterminateSystems installer supports `aarch64-linux` as well, so adding `linux/arm64` builds in the future would not be blocked by this change. → **Decision:** Defer to future. Out of scope for this fix.
- [RESOLVED] **Nix version pinning:** Consider pinning the Nix version in the Dockerfile for reproducibility, either via the installer version tag or a `NIX_VERSION` build arg. → **Decision:** Add a `NIX_VERSION` build arg to the Dockerfile for optional version pinning. This provides reproducibility without mandating it.

## New Issues (from cross-check)

- [RESOLVED] **NIX_VERSION build arg semantics:** The DeterminateSystems install URL does not accept a Nix version parameter directly — the Nix version is determined by the installer release. To pin a version, the URL changes to `install.determinate.systems/nix/tag/v<VERSION>` where VERSION is the *installer* version (e.g. `0.31.1`), not the Nix version. The build arg should either be named `NIX_INSTALLER_VERSION` to reflect this, or the plan should clarify how the mapping from installer version to Nix version works. → **Decision:** Drop the build arg entirely. Always use the latest installer. This avoids the confusing naming issue and aligns with the earlier decision not to pin the installer version.
