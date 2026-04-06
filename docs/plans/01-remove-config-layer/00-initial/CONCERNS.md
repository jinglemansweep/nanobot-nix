# Concerns

> Source: `plans/01-config-expansion/00-initial/PROMPT.md`

## Previous Concerns (Invalidated)

All concerns from the original expansion plan are invalidated — the plan direction has changed from expanding the mapping layer to removing it entirely.

- ~~Mochat `groups` field as JSON blob vs skip~~ — No mapping layer; Pydantic handles it natively.
- ~~OAuth provider aliases (`openai_codex`, `github_copilot`)~~ — No alias system.
- ~~DEFAULTS model update (`claude-opus-4-5` vs `claude-sonnet-4-5`)~~ — No DEFAULTS override; upstream defaults apply.
- ~~DEFAULTS not documented in Components section~~ — DEFAULTS removed entirely.
- ~~Prefix change requires `config_generate.py` changes~~ — `config_generate.py` is being deleted.
- ~~Prefix rename breaking change for `.env` files~~ — Env var format is changing regardless (see Breaking Changes below).
- ~~Schema drift / upstream schema changes~~ — No mapping to drift; users use Pydantic env vars directly.
- ~~Env var explosion in `.env.example`~~ — `.env.example` documents common fields only; full coverage is inherent via Pydantic.
- ~~Keep mapping layer for aliases/coercion/defaults~~ — Decision reversed: remove mapping layer entirely.
- ~~Region-specific channel docs language~~ — Still English-only; brief comments noting regional channels remain.

## Open Questions

- [RESOLVED] **Exact Python field names:** The upstream schema field names (snake_case) must be verified before writing `.env.example`. → **Decision:** Verified by fetching upstream `schema.py`. All field names confirmed and recorded in RESEARCH.md. Fields use snake_case (e.g., `api_key`, `allow_from`, `bot_token`, `extra_headers`). Notable finding: Slack has no top-level `allow_from` — only `group_allow_from` and `dm.allow_from`.
- [RESOLVED] **Config file vs env var priority:** Whether `nanobot onboard` creates a `config.json` that conflicts with env var config. → **Decision:** Assume env vars take priority. Pydantic `BaseSettings` prioritises env vars over file config by default. No special handling needed in the entrypoint.

## Breaking Changes

These changes affect existing users upgrading from the current mapping layer:

| Change | Before | After |
|--------|--------|-------|
| Env var delimiter | Single `_` (`NANOBOT_PROVIDERS_ANTHROPIC_APIKEY`) | Double `__` (`NANOBOT_PROVIDERS__ANTHROPIC__API_KEY`) |
| Field naming | camelCase-derived (`APIKEY`, `ALLOWFROM`) | snake_case-derived (`API_KEY`, `ALLOW_FROM`) |
| List values | CSV (`user1,user2`) | JSON array (`["user1","user2"]`) |
| Aliases | Supported (`ANTHROPIC_API_KEY`) | Removed — use canonical names only |
| Default model override | Custom DEFAULTS in schema | Upstream default applies |
| Docker secret file names | `NANOBOT_PROVIDERS_ANTHROPIC_APIKEY` | `NANOBOT_PROVIDERS__ANTHROPIC__API_KEY` |

## Risks

- [RESOLVED] **User confusion with `__` delimiter:** The double underscore delimiter is less intuitive than single underscore. → **Decision:** Documentation is sufficient mitigation. Clear examples in `.env.example` and `README.md`. This is standard Pydantic convention.
- [RESOLVED] **JSON array syntax is less ergonomic:** `["user1","user2"]` is harder to type than `user1,user2` for `allow_from` lists. → **Decision:** Accept the trade-off. JSON arrays are the standard Pydantic way. No custom shim needed.
- [RESOLVED] **Undocumented field names:** Risk of wrong field names causing silent failures. → **Decision:** Resolved. Field names verified by fetching upstream `schema.py` and recorded in RESEARCH.md.
