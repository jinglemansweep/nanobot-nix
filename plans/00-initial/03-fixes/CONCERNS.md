# Concerns

> Source: `.agent/plans/04-testing-02/PROMPT.md`

## Open Questions

- [RESOLVED] The user's env vars use `ZHIPU` as the provider name. Upstream Nanobot's config.json provider key should be `zhipu` to match — confirm this is how the Nanobot runtime resolves provider routing (i.e., it uses the key under `providers.*` to dispatch API calls with the correct base URL and auth). → **Decision:** Use `zhipu` as the provider key. Matches existing env var naming and the convention of other providers (company name, not model family).

## Potential Blockers

- No potential blockers identified. This is a data-only change to the schema file, following an established pattern with five existing providers as precedent.

## Risks

- [RESOLVED] If the Zhipu API base URL differs between Chinese and international endpoints (`open.bigmodel.cn` vs `api.z.ai`), users must set `NANOBOT_PROVIDERS_ZHIPU_APIBASE` explicitly for the correct region. There is no way to auto-detect this — but this is the same trade-off already made for all other providers that support `apiBase`. → **Decision:** Default to the international Coding Plan endpoint (`https://api.z.ai/api/coding/paas/v4`). China users or non-Coding-Plan users override via `NANOBOT_PROVIDERS_ZHIPU_APIBASE`.

## Future Considerations

- [RESOLVED] Zhipu has a separate "Coding Plan" API endpoint (`api.z.ai/api/coding/paas/v4`) and an Anthropic-protocol endpoint (`api.z.ai/api/anthropic`). If users need these, they can set them via `NANOBOT_PROVIDERS_ZHIPU_APIBASE` or use the `CUSTOM` provider. No special handling is needed now. → **Decision:** The Coding Plan endpoint (`https://api.z.ai/api/coding/paas/v4`) is the most common use case and is now the default API base URL. Non-Coding-Plan users can override via APIBASE.
- [RESOLVED] If additional Zhipu-specific config fields are needed in the future (e.g., coding plan subscription tier), they can be added to `ENV_MAP` following the same pattern. → **Decision:** Deferred. The pattern is established and extensible; add fields when there's an actual need.
