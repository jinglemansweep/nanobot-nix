# Task List

> Source: `.agent/plans/05-testing/PLAN.md`

## Array Field Type Inference Fix

### Fix `infer_type()` Precedence

- [x] **Move array field check before numeric conversion in `infer_type()`** — In `scripts/config_generate.py`, modify the `infer_type(suffix, value)` function (currently lines 42–63). Insert a new block immediately after the bool check (line 45) and before the `int()` attempt (line 47). The new block should be:
  ```python
  if suffix in ARRAY_FIELDS:
      if "," in value:
          return [item.strip() for item in value.split(",")]
      return [value]
  ```
  Remove the existing array field check at lines 60–61 (`if suffix in ARRAY_FIELDS and "," in value:`), since the new block now handles both single-value and multi-value cases. The final `infer_type()` order should be: bool → array field → int → float → JSON → string. Verify by running `pytest tests/test_config_generate.py` — existing tests for bool, int (non-array), float, JSON, CSV array, and plain string should all still pass (the `test_infer_type_int` test uses `"SOME_FIELD"` which is not in `ARRAY_FIELDS`, so it is unaffected).

## Bug-Specific Unit Tests

### Single-Value Array Field Tests

- [x] **Add test for single numeric value in array field** — In `tests/test_config_generate.py`, add a new test function `test_infer_type_single_numeric_array_field` that calls `infer_type("CHANNELS_DISCORD_ALLOWFROM", "701044353249837097")` and asserts the result equals `["701044353249837097"]`. Also assert `isinstance(result, list)` to confirm it is a list, not an int. This directly reproduces the bug from the error report.

- [x] **Add test for single non-numeric value in array field** — In `tests/test_config_generate.py`, add a new test function `test_infer_type_single_string_array_field` that calls `infer_type("CHANNELS_TELEGRAM_ALLOWFROM", "alice")` and asserts the result equals `["alice"]`. Also assert `isinstance(result, list)`. This ensures single non-numeric values are also wrapped in a list.

- [x] **Add test for multi-value numeric array field** — In `tests/test_config_generate.py`, add a new test function `test_infer_type_csv_numeric_array_field` that calls `infer_type("CHANNELS_DISCORD_ALLOWFROM", "123456789,987654321")` and asserts the result equals `["123456789", "987654321"]`. This verifies that comma-separated numeric values in array fields remain as strings (not converted to ints) and are properly split.

## Full Pipeline Integration Test

### Discord `allowFrom` End-to-End Test

- [ ] **Add integration test reproducing the exact bug scenario** — In `tests/test_config_generate.py`, add a new test function `test_generate_discord_allowfrom_single_id` following the pattern of the existing `test_generate_full_pipeline` test. The test should:
  1. Use `monkeypatch` and `tmp_path` fixtures.
  2. Set `HOME` to `str(tmp_path)`.
  3. Set the following env vars via `monkeypatch.setenv()`:
     - `NANOBOT_CHANNELS_DISCORD_ENABLED` = `"true"`
     - `NANOBOT_CHANNELS_DISCORD_TOKEN` = `"test-discord-token"`
     - `NANOBOT_CHANNELS_DISCORD_ALLOWFROM` = `"123444351234838888"`
  4. Remove all other `NANOBOT_*` env vars (loop over `os.environ.keys()` and `monkeypatch.delenv()` any that start with `NANOBOT_` but aren't the three above).
  5. Patch `read_docker_secrets` to a no-op: `monkeypatch.setattr("scripts.config_generate.read_docker_secrets", lambda: None)`.
  6. Create `tmp_path / ".nanobot"` directory.
  7. Call `generate()`.
  8. Read and parse `tmp_path / ".nanobot" / "config.json"`.
  9. Assert `config["channels"]["discord"]["enabled"]` is `True`.
  10. Assert `config["channels"]["discord"]["token"]` equals `"test-discord-token"`.
  11. Assert `config["channels"]["discord"]["allowFrom"]` equals `["123444351234838888"]` — this is the critical assertion that validates the fix.
  12. Assert `isinstance(config["channels"]["discord"]["allowFrom"], list)` for explicit type checking.

## Verification

### Run Full Test Suite

- [ ] **Run `pre-commit run --all-files` and fix any issues** — Activate the virtualenv (`source .venv/bin/activate`) and run `pre-commit run --all-files`. Fix any linting, formatting, or other errors until the command passes cleanly.

- [ ] **Run `pytest` and verify all tests pass** — Run `pytest tests/test_config_generate.py -v` and confirm all tests pass, including the new tests added above and all pre-existing tests. Expected test count: the existing tests (approximately 14) plus 4 new tests = approximately 18 total. Zero failures, zero skips.
