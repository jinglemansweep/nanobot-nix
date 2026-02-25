# Task List

> Source: `.agent/plans/02-initial-fixes/PLAN.md`

## Docker Compose Local Build Support

- [x] **Add build configuration to `docker-compose.yml`** — Add an `x-common-build` YAML anchor at the top of `docker-compose.yml` that defines a shared build configuration. The anchor should specify `context: .` (project root), `dockerfile: Dockerfile`, and `args:` with `NANOBOT_REPO: https://github.com/HKUDS/nanobot.git` and `NANOBOT_REF: main`. Then reference this anchor in both the `gateway` and `cli` services using `build: *common-build`. Keep the existing `image:` keys intact on both services so `docker compose pull` and default `docker compose up` continue to use the GHCR image, while `docker compose build` and `docker compose up --build` will build locally. Verify by running `docker compose config` and confirming both services show `build:` and `image:` keys with correct values.

## Python Package Structure

- [x] **Create `scripts/__init__.py`** — Create an empty file at `scripts/__init__.py` to make the `scripts/` directory a proper Python package. The file should be empty (no content needed). Verify the file exists: `ls scripts/__init__.py`.

- [x] **Convert `config_generate.py` to use relative import** — In `scripts/config_generate.py`, change line 9 from `from config_schema import ALIASES, ARRAY_FIELDS, DEFAULTS, ENV_MAP` to `from .config_schema import ALIASES, ARRAY_FIELDS, DEFAULTS, ENV_MAP`. This enables importing the module as `scripts.config_generate` from the project root. Verify by running `python3 -c "from scripts.config_generate import generate"` from the project root.

- [x] **Add `WORKDIR` to Dockerfile** — In `Dockerfile`, add `WORKDIR /opt/nanobot-nix` on a new line immediately before the `ENTRYPOINT` directive (before line 69). This sets the working directory so `python3 -m scripts.config_generate` resolves the package correctly at runtime.

- [x] **Update entrypoint.sh Python invocation** — In `scripts/entrypoint.sh`, change line 15 from `python3 /opt/nanobot-nix/scripts/config_generate.py` to `python3 -m scripts.config_generate`. The `WORKDIR` in the Dockerfile ensures the working directory is `/opt/nanobot-nix`, so the module path resolves correctly.

- [x] **Create `pyproject.toml`** — Create `pyproject.toml` at the project root with the following content:
  - `[build-system]` section with `requires = ["setuptools>=68.0"]` and `build-backend = "setuptools.backends._legacy:_Backend"`
  - `[project]` section with `name = "nanobot-nix"`, `version = "0.1.0"`, `requires-python = ">=3.11"`
  - `[project.optional-dependencies]` section with `dev = ["pytest"]`
  - `[tool.setuptools.packages.find]` section with `include = ["scripts*"]`
  - Verify by running `pip install -e ".[dev]"` and confirming pytest is available.

## Shellcheck Pre-commit Integration

- [x] **Add shellcheck hook to `.pre-commit-config.yaml`** — Append a new repo entry to `.pre-commit-config.yaml` after the existing `pre-commit-hooks` repo block. Add:
  ```yaml
  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.10.0.1
    hooks:
      - id: shellcheck
  ```
  Verify by running `pre-commit run shellcheck --all-files` and observing it runs against the shell scripts (it may report warnings that need fixing — see next tasks).

- [x] **Fix shellcheck warnings in `scripts/nix-install.sh`** — Run `pre-commit run shellcheck --all-files` and fix all warnings in `scripts/nix-install.sh`. Known issue: line 22 uses `echo "$entry" | xargs` for whitespace trimming, which shellcheck flags. Replace with a bash parameter expansion pattern: use `trimmed="${entry#"${entry%%[![:space:]]*}"}"` followed by `trimmed="${trimmed%"${trimmed##*[![:space:]]}"}"` (or an equivalent shell-native trimming approach). Fix any other warnings reported. Verify by re-running `pre-commit run shellcheck --all-files` and confirming no warnings for this file.

- [x] **Fix shellcheck warnings in `scripts/entrypoint.sh`** — Run shellcheck against `scripts/entrypoint.sh` and fix all warnings. Potential issues: the `source` command on line 6 (`. /root/.nix-profile/etc/profile.d/nix.sh`) may trigger SC1091 (not following sourced file). If shellcheck cannot follow the path, add a directive `# shellcheck source=/dev/null` above the line only if the warning is about a file that doesn't exist in the repo context. Fix any other warnings. Verify by re-running `pre-commit run shellcheck --all-files` with no warnings for this file.

- [x] **Fix shellcheck warnings in `scripts/nix-search.sh`** — Run shellcheck against `scripts/nix-search.sh` and fix all warnings. Potential issue: line 13 uses `&>/dev/null` which is valid bash but shellcheck may flag patterns related to the `nix search` command or quoting. Fix any reported issues. Verify by re-running `pre-commit run shellcheck --all-files` with no warnings for this file.

## Pytest Test Suite

### Schema Tests

- [x] **Create `tests/test_config_schema.py`** — Create `tests/test_config_schema.py` with tests that validate the data structures in `scripts/config_schema.py`. Import via `from scripts.config_schema import ENV_MAP, DEFAULTS, ARRAY_FIELDS, ALIASES`. Include the following test functions:
  - `test_env_map_values_are_tuples` — Assert every value in `ENV_MAP` is a `tuple` and has at least one element.
  - `test_env_map_values_contain_strings` — Assert every element in each `ENV_MAP` tuple is a `str`.
  - `test_array_fields_exist_in_env_map` — Assert every key in `ARRAY_FIELDS` also exists as a key in `ENV_MAP`.
  - `test_aliases_point_to_valid_canonical_names` — Assert every value in `ALIASES` starts with `"NANOBOT_"` and that the suffix (after removing `"NANOBOT_"`) exists as a key in `ENV_MAP`.
  - `test_defaults_is_dict` — Assert `DEFAULTS` is a `dict`.
  - `test_no_duplicate_env_map_paths` — Assert no two keys in `ENV_MAP` map to the same tuple path.
  - Verify by running `pytest tests/test_config_schema.py -v` and confirming all tests pass.

### Generate Tests

- [x] **Create `tests/test_config_generate.py`** — Create `tests/test_config_generate.py` with unit tests for the functions in `scripts/config_generate.py`. Import via `from scripts.config_generate import infer_type, set_nested, resolve_aliases, read_docker_secrets, generate`. Include the following test functions:
  - `test_infer_type_bool_true` — Call `infer_type("SOME_FIELD", "true")` and assert result is `True` (Python bool).
  - `test_infer_type_bool_false` — Call `infer_type("SOME_FIELD", "false")` and assert result is `False`.
  - `test_infer_type_int` — Call `infer_type("SOME_FIELD", "42")` and assert result is `42` (int).
  - `test_infer_type_float` — Call `infer_type("SOME_FIELD", "3.14")` and assert result is `3.14` (float).
  - `test_infer_type_json_object` — Call `infer_type("SOME_FIELD", '{"key": "val"}')` and assert result is `{"key": "val"}`.
  - `test_infer_type_json_array` — Call `infer_type("SOME_FIELD", '[1, 2]')` and assert result is `[1, 2]`.
  - `test_infer_type_csv_array_field` — Call `infer_type("CHANNELS_TELEGRAM_ALLOWFROM", "alice, bob, charlie")` and assert result is `["alice", "bob", "charlie"]`.
  - `test_infer_type_csv_non_array_field` — Call `infer_type("SOME_FIELD", "a, b, c")` and assert result is the raw string `"a, b, c"` (no splitting because `"SOME_FIELD"` is not in `ARRAY_FIELDS`).
  - `test_infer_type_plain_string` — Call `infer_type("SOME_FIELD", "hello")` and assert result is `"hello"`.
  - `test_set_nested_creates_path` — Start with `config = {}`, call `set_nested(config, ("a", "b", "c"), "val")`, assert `config == {"a": {"b": {"c": "val"}}}`.
  - `test_set_nested_overwrites` — Start with `config = {"a": {"b": "old"}}`, call `set_nested(config, ("a", "b"), "new")`, assert `config == {"a": {"b": "new"}}`.
  - `test_resolve_aliases(monkeypatch)` — Use `monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")` and ensure `NANOBOT_PROVIDERS_OPENROUTER_APIKEY` is NOT set. Call `resolve_aliases()`. Assert `os.environ["NANOBOT_PROVIDERS_OPENROUTER_APIKEY"] == "test-key"`. Clean up with `monkeypatch.delenv`.
  - `test_resolve_aliases_does_not_overwrite(monkeypatch)` — Set both `OPENROUTER_API_KEY=alias-val` and `NANOBOT_PROVIDERS_OPENROUTER_APIKEY=canonical-val`. Call `resolve_aliases()`. Assert `os.environ["NANOBOT_PROVIDERS_OPENROUTER_APIKEY"] == "canonical-val"` (canonical is not overwritten).
  - `test_read_docker_secrets(monkeypatch, tmp_path)` — Create a file `tmp_path / "NANOBOT_TEST_SECRET"` with content `"secret-value\n"`. Use `monkeypatch.setattr("scripts.config_generate.read_docker_secrets.__code__", ...)` — actually, better approach: monkeypatch the `secrets_dir` variable. Since `secrets_dir` is a local variable, instead monkeypatch `os.path.isdir` to return `True` for the tmp_path, and `os.listdir` to return `["NANOBOT_TEST_SECRET"]`, and use `monkeypatch.setattr` to make `os.path.join` return the temp file path. Simpler approach: set the env before calling and patch the hardcoded `/run/secrets` path — or just create a direct test that patches the function's `secrets_dir`. The cleanest approach is to just test the function by monkeypatching: set `os.path.isdir` to return True for `/run/secrets`, use `tmp_path` to create the secret file, and patch `os.listdir` and `os.path.join` for the secrets dir. Assert the env var is set after calling the function.
  - `test_generate_full_pipeline(monkeypatch, tmp_path)` — Use `monkeypatch.setenv("HOME", str(tmp_path))` so `os.path.expanduser("~")` resolves to `tmp_path`. Set `monkeypatch.setenv("NANOBOT_PROVIDERS_OPENROUTER_APIKEY", "test-key-123")`. Create `tmp_path / ".nanobot"` directory. Call `generate()`. Read `tmp_path / ".nanobot" / "config.json"` and parse as JSON. Assert it contains `{"providers": {"openrouter": {"apiKey": "test-key-123"}}}` merged with the defaults. Also assert the `agents.defaults.model` default value is present.
  - Verify by running `pytest tests/test_config_generate.py -v` and confirming all tests pass.

## CI Test Workflow

- [x] **Create `.github/workflows/test.yml`** — Create `.github/workflows/test.yml` with a GitHub Actions workflow that runs on pull requests and pushes to `main`. Use the following structure:
  - `name: Test`
  - `on:` trigger on `push: branches: [main]` and `pull_request:`
  - `permissions: contents: read`
  - Single job `test:` running on `ubuntu-latest`
  - Steps:
    1. `actions/checkout@v4`
    2. `actions/setup-python@v5` with `python-version: "3.11"`
    3. `pip install -e ".[dev]"` — install project with dev dependencies
    4. `pip install pre-commit` — install pre-commit
    5. `pre-commit run --all-files` — run all pre-commit hooks
    6. `pytest -v` — run the test suite
  - Verify by reviewing the YAML with `python -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))"` (if PyYAML is available) or by running `check-yaml` pre-commit hook.

## Documentation Skill

- [x] **Create `.claude/skills/documentation/SKILL.md`** — Create the file `.claude/skills/documentation/SKILL.md` defining a documentation audit skill. The skill should instruct the agent to:
  1. **Inventory** — List all documentation files: `README.md`, `CLAUDE.md`, `.env.example`, all `SKILL.md` files under `.claude/skills/`, and significant inline documentation (Python docstrings, shell script comments).
  2. **Cross-reference code** — For each documentation file:
     - Verify all environment variable names mentioned match keys in `scripts/config_schema.py`'s `ENV_MAP` and `ALIASES`.
     - Verify all file paths, directory references, and command examples actually exist and work.
     - Verify all build arguments, Docker image names, and port numbers match `Dockerfile` and `docker-compose.yml`.
     - Verify feature descriptions match actual code behavior.
  3. **Identify gaps** — Check for:
     - Features present in code but missing from documentation.
     - Deprecated or removed features still mentioned in documentation.
     - Inconsistencies between different documentation files (e.g., README says one thing, .env.example says another).
  4. **Report and fix** — Produce a summary of findings (accurate items, stale items, missing items) and apply fixes directly to the documentation files.
  - The skill should use `Read`, `Glob`, and `Grep` tools to explore the codebase, and `Edit` to apply fixes.
  - The skill should be invocable as `/documentation`.
  - Verify by confirming the file exists at `.claude/skills/documentation/SKILL.md` and is well-formed markdown.

## CLAUDE.md Updates

- [x] **Add pytest to quality gate instructions in `CLAUDE.md`** — In `CLAUDE.md`, update the Quality Gates section. After the existing bullet about `pre-commit run --all-files`, modify the second bullet to explicitly mention pytest: change `If any test suites exist in the project, run ALL tests and resolve ALL failures before proceeding. No skipped or ignored tests.` to `Run \`pytest\` and resolve ALL test failures before proceeding. No skipped or ignored tests.`. This makes the test command explicit rather than conditional.

- [x] **Add documentation skill invocation rule to `CLAUDE.md`** — In `CLAUDE.md`, add a new section after the Git section:
  ```markdown
  ## Documentation

  - After completing a large unit of work or before a large commit, run the `/documentation` skill to audit all project documentation for accuracy and completeness.
  ```
  Verify by reading the updated `CLAUDE.md` and confirming both changes are present.

## Final Validation

- [ ] **Run pre-commit and pytest** — Run `pre-commit run --all-files` and fix any remaining issues. Then run `pytest -v` and ensure all tests pass. This is the quality gate defined in `CLAUDE.md` — both commands must pass cleanly with zero errors and zero warnings before the work is considered complete.
