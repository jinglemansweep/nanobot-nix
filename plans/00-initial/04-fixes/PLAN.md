# Implementation Plan

> Source: `.agent/plans/05-testing/PROMPT.md`

## Overview

Fix the `allowFrom` array field bug where single-value environment variables (e.g. Discord user IDs) are type-inferred as integers instead of lists, causing Pydantic validation failures in upstream Nanobot. Add comprehensive tests to cover the bug scenario and prevent regressions.

## Architecture & Approach

The root cause is in `scripts/config_generate.py:infer_type()`. The function's type inference precedence is: bool → int → float → JSON → CSV array → string. When a field like `CHANNELS_DISCORD_ALLOWFROM` contains a single numeric value (e.g. `701044353249837097`), it matches `int()` conversion at step 2 and never reaches the array field check at step 5.

The fix is to check whether a suffix belongs to `ARRAY_FIELDS` **before** any other type inference. If it does, the value should always be returned as a list — either by splitting on commas (for multi-value) or by wrapping the single value in a list. Values within array fields should remain as strings (since `allowFrom` expects `list[str]`).

This also fixes a secondary edge case: comma-separated numeric values like `"123,456"` currently produce `["123", "456"]` (strings in a list), but a single numeric value produces `701044353249837097` (bare int). The fix makes both cases consistent: always `list[str]`.

## Components

### Array Field Type Inference Fix

**Purpose:** Ensure `ARRAY_FIELDS` entries always produce `list[str]` values regardless of input format.

**Inputs:** The `suffix` and `value` parameters passed to `infer_type()`.

**Outputs:** A `list[str]` when `suffix` is in `ARRAY_FIELDS`; unchanged behavior for all other fields.

**Notes:** The check must be placed before the int/float/JSON conversion attempts. For array fields: if the value contains commas, split and strip; otherwise, wrap the single value as `[value]`. No numeric conversion should be attempted on array field values. This is a minimal change — only the ordering/precedence within `infer_type()` changes, not the function signature or any callers.

### Bug-Specific Test Coverage

**Purpose:** Add tests that directly reproduce the reported bug scenario and verify the fix.

**Inputs:** Test cases using realistic Discord user IDs and single-value array field inputs.

**Outputs:** Passing tests that assert single-value array fields produce `list[str]`.

**Notes:** The existing test `test_infer_type_csv_array_field` only covers the multi-value comma-separated case (`"alice, bob, charlie"`). New tests must cover: (1) single numeric value in an array field, (2) single non-numeric value in an array field, (3) the full pipeline with a realistic Discord `allowFrom` setup matching the error report. The existing `test_infer_type_int` test for non-array fields must continue to pass (numeric inference is still correct for non-array fields).

### Full Pipeline Integration Test

**Purpose:** Reproduce the exact scenario from the error report end-to-end — Discord channel with `enabled`, `token`, and a single numeric `allowFrom` — and verify the generated config.json is valid.

**Inputs:** Environment variables matching the prompt's `.env` example (with sanitized values).

**Outputs:** A generated config.json where `channels.discord.allowFrom` is `["123444351234838888"]` (list of strings), not `123444351234838888` (int).

**Notes:** This test validates the full `generate()` pipeline, not just `infer_type()`, ensuring the fix works through the entire code path including `set_nested()` and JSON serialization.

## File Manifest

| File | Action | Purpose |
|------|--------|---------|
| `scripts/config_generate.py` | Modify | Reorder `infer_type()` to check `ARRAY_FIELDS` before numeric conversion |
| `tests/test_config_generate.py` | Modify | Add tests for single-value array fields and full Discord pipeline |
