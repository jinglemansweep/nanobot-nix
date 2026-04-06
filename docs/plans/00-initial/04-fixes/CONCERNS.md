# Concerns

> Source: `.agent/plans/05-testing/PROMPT.md`

## Open Questions

- None. The bug is clear and the fix is straightforward.

## Potential Blockers

- None identified.

## Risks

- **Semantic change for array fields:** After the fix, a value like `"42"` set on an array field will become `["42"]` instead of `42`. This is the correct behavior (Nanobot expects `list[str]`), but any downstream tooling that was accidentally relying on the broken numeric output would need updating. Given that the current behavior causes a startup crash, this is not a practical risk.

## Future Considerations

- **Typed array elements:** Currently array field values are always `list[str]`. If upstream Nanobot ever introduces array fields that expect `list[int]` (e.g. numeric user IDs as integers), the array splitting logic would need per-field element type casting. This is not needed today — Nanobot's `allowFrom` expects `list[str]`.
- **Space-separated lists:** The current CSV parsing only splits on commas. If users expect space-separated values (common in shell contexts), this could be a future enhancement. Not relevant to the current bug.
