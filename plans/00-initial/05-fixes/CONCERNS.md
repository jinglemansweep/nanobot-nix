# Concerns

> Source: `.agent/plans/06-testing/PROMPT.md`

## Open Questions

- [RESOLVED] What exact value does `NANOBOT_NIX_ALLOWED_PACKAGES` have in the user's `.env` file? If it's `*` (unquoted in the env file), it may be subject to shell expansion depending on how docker-compose processes the `env_file` directive. This needs verification. → **Decision:** Value is `NANOBOT_NIX_ALLOWED_PACKAGES="*"` (quoted asterisk). Shell expansion of `*` is a confirmed risk that tests must cover.
- [RESOLVED] Is the `*` directory appearing from the built-in skills glob (`/opt/nanobot-nix/skills/*/`) or the custom skills glob (`/mnt/skills/*/`)? Knowing which glob misfires would narrow the fix. → **Decision:** Not sure which glob — fix both. Apply the nullglob guard to both glob loops regardless of which is the actual culprit.
- [RESOLVED] How much change to the Docker/container setup is acceptable for the user/permissions issue? The prompt says "don't change the container setup too much" but doesn't define the boundary. → **Decision:** Document only. No Dockerfile or docker-compose changes. Record findings and recommendations in this file for future work.

## Potential Blockers

- [RESOLVED] Testing shell scripts that depend on `nix` and `nanobot` binaries requires stubbing those commands. If the scripts use features that are hard to stub (e.g., `nix profile list` output parsing), tests may need to be more involved or skip those paths. → **Decision:** Extract testable functions. Refactor shell scripts to extract pure logic (whitelist checking, glob handling) into sourced helper functions that can be tested without the full script flow.

## Risks

- [RESOLVED] The `nullglob` fix, while correct, changes bash glob behavior for the entire scope where it's active. If future additions to `entrypoint.sh` rely on default glob behavior (non-matching globs preserved), they could silently break. Scoping `nullglob` tightly mitigates this. → **Decision:** Scope tightly. Set nullglob before the glob loops and unset immediately after to prevent affecting other parts of the script.
- [RESOLVED] Shell script tests using `subprocess` are inherently slower and more fragile than pure Python tests. They depend on the system's bash version and may behave differently in CI vs local environments. → **Decision:** Source + test in bash via pytest. Tests source the helper functions and invoke them directly via `bash -c` calls. Small and fast since they only call shell functions, not full scripts.

## Docker User/Permissions

1. **Why the container runs as root:** The Dockerfile has no `USER` directive, so all processes run as root. This is currently necessary because:
   - Nix (installed via DeterminateSystems installer) requires root for single-user mode installation and package operations.
   - The workspace is located at `/root/.nanobot/`, which is the root user's home directory.
   - Various tools (apt, npm, pip) used during the build expect root permissions.

2. **Host file ownership conflicts:** When users mount local directories into the container (e.g. `./skills:/mnt/skills`), any files created by the container on writable bind mounts are owned by `root:root` on the host. This can cause permission conflicts when the host user tries to read, modify, or delete those files.

3. **Recommended future approach:** To run as a non-root user:
   - Create a dedicated user (e.g. `nanobot`) in the Dockerfile.
   - Configure Nix in single-user mode for that user (install to the user's profile rather than the system profile).
   - Move the workspace from `/root/.nanobot/` to `/home/nanobot/.nanobot/`.
   - Update the `docker-compose.yml` volumes to use the new path.
   - Use the `USER` directive in the Dockerfile or `--user` flag at runtime.
   - This is a significant change that warrants its own implementation plan.

4. **Interim mitigation:** The `:ro` (read-only) flag on the skill mount (`./skills:/mnt/skills:ro`) prevents the container from modifying host skill files. The `nanobot-data` and `nix-store` volumes are Docker-managed named volumes, so root ownership there does not affect the host filesystem. However, any files written to user-added writable bind mounts will still be root-owned on the host.

## Future Considerations

- [RESOLVED] The container running as root is a genuine operational concern for anyone mounting local files. A proper fix (non-root user, Nix single-user mode, adjusted paths) would be a significant change warranting its own plan. → **Decision:** Document only for now. This is out of scope for this plan and should get its own plan when prioritized.
- [RESOLVED] As more shell scripts are added, a shell testing framework like `bats-core` may be more appropriate than pytest+subprocess. For now, the two scripts are simple enough that pytest works. → **Decision:** Pytest for now, revisit later. If more shell scripts are added, consider migrating to bats-core at that point.
- [RESOLVED] The entrypoint's skill-symlinking logic could be extracted into its own script for better testability and reuse. → **Decision:** Yes — extract now. Extract the skill-symlinking logic into a helper script (e.g., `scripts/link-skills.sh`). Aligns with the decision to extract testable functions.
