# Concerns

> Source: `.agent/plans/01-initial/PROMPT.md`

## Open Questions

- [RESOLVED] **Nix installation strategy in multi-stage build:** Should Nix be installed in the builder stage and the `/nix` directory copied to runtime, or installed directly in the runtime stage? → **Decision:** Install directly in the runtime stage. Simpler Dockerfile, avoids cross-stage `/nix` copy complexity. Adds ~2 min to build time which is acceptable.
- [RESOLVED] **Nix channel pinning:** The prompt doesn't specify which Nix channel or nixpkgs revision to use. → **Decision:** Use `nixpkgs-unstable` rolling channel. Packages are always current. Non-deterministic across builds is acceptable since the image is rebuilt weekly anyway — freshness matters more than pinning.
- [RESOLVED] **WhatsApp bridge runtime:** The bridge is built in the builder stage, but how is it started at runtime? → **Decision:** User responsibility. The entrypoint does not auto-start the bridge. Users who need WhatsApp can run it separately via docker compose or a sidecar. Keeps the entrypoint simple and avoids process supervision complexity.
- [RESOLVED] **`nanobot onboard` idempotency:** The entrypoint runs `nanobot onboard` if no workspace exists. → **Decision:** Guard with a check for `~/.nanobot/workspace/` directory. Only run onboard if it doesn't exist. Config.json gets overwritten by the generator regardless, so onboard's main value is creating the workspace structure and template files.

## Potential Blockers

- [RESOLVED] **Multi-arch Nix installation:** Nix must install correctly on both `linux/amd64` and `linux/arm64` within the Docker build. QEMU-emulated builds can be slow and flaky. → **Decision:** Drop arm64 for the initial build. Build `linux/amd64` only. Can add arm64 later if needed. Eliminates QEMU flakiness and reduces CI build time.
- [RESOLVED] **Image size:** Combining Python, Node.js 20, Nix, and apt tools will produce a large image (1-2GB+). → **Decision:** Accept it. This is an inherent trade-off of the "batteries-included" approach. The image is pulled once and cached. Prioritise functionality over size.

## Risks

- [RESOLVED] **Upstream breaking changes:** Nanobot is under very rapid development. Tracking `main` means the weekly build could break. → **Decision:** Accept it, pin on failure. Track main as designed (Decision 5). If a weekly build breaks, manually pin `NANOBOT_REF` to the last known good commit via workflow dispatch. No extra infrastructure needed.
- [RESOLVED] **Nix store growth:** The `/nix` volume will grow indefinitely as the agent installs packages. → **Decision:** Add Nix garbage collection instructions to the toolbox skill. The agent can be informed about `nix-collect-garbage -d` and when to use it. Also document manual GC in the README.
- [RESOLVED] **Config generator type inference edge cases:** The type inference logic could misinterpret values. → **Decision:** Accept current logic. The current ENV_MAP fields are all strings (API keys, URLs) or known types (booleans for enabled, arrays for allowFrom). Edge cases are theoretical for the current schema. Can add explicit type hints later only if a real problem surfaces.

## Future Considerations

- [RESOLVED] **Nix flake-based provisioning:** The current design uses `nix-env` for imperative package installation. → **Decision:** Deferred. Using `nixpkgs-unstable` channel with imperative `nix-env` for now. Flake-based provisioning can be evaluated in a future iteration.
- [RESOLVED] **Health checks:** The Docker Compose file doesn't include health checks. → **Decision:** Add to initial scope. Add a healthcheck to the gateway service in `docker-compose.yml` hitting the gateway's HTTP endpoint on port 18790.
- [RESOLVED] **Multi-container bridge:** If the WhatsApp bridge needs to run as a separate process, it could be split into its own container. → **Decision:** Deferred. Aligns with the WhatsApp bridge decision — it's the user's responsibility to run the bridge. A dedicated compose service can be added later if demand warrants it.
- [RESOLVED] **Config validation:** The config generator writes JSON without validating it against Nanobot's Pydantic schema. → **Decision:** Deferred. The generator produces well-formed JSON and Nanobot validates on startup anyway. Adding validation would couple the generator to Nanobot's internals, contradicting the schema-agnostic design.
- [RESOLVED] **Secret management:** The current design passes secrets via environment variables and `.env` files. → **Decision:** Add Docker secrets support to the initial scope. Extend `config_generate.py` to read from `/run/secrets/*` as an alternative to env vars. If a file exists at `/run/secrets/NANOBOT_<KEY>`, its contents are used as the value.
