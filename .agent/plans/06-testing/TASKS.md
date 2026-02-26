# Task List

> Source: `.agent/plans/06-testing/PLAN.md`

## Entrypoint Glob Fix

### Extract Skill-Linking Logic

- [x] **Create `scripts/link-skills.sh`** — Create a new file `scripts/link-skills.sh` with a function `link_skills` that accepts two arguments: `builtin_skills_dir` and `custom_skills_dir`, plus a third argument `target_dir` for the symlink destination. The function must:
  1. Run `mkdir -p "$target_dir"`
  2. Set `shopt -s nullglob` before any glob expansion
  3. Loop over `"$builtin_skills_dir"/*/` and create symlinks in `"$target_dir"` via `ln -sfn "$dir" "$target_dir/$(basename "$dir")"`
  4. If `"$custom_skills_dir"` exists (`[ -d "$custom_skills_dir" ]`), loop over `"$custom_skills_dir"/*/` and create symlinks the same way (custom overrides built-in of the same name)
  5. Set `shopt -u nullglob` after both loops complete
  6. The file should have a shebang `#!/usr/bin/env bash` and `set -euo pipefail`, and guard execution so it only defines the function when sourced (use `if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then link_skills "$@"; fi` at the bottom so it can also be called directly)
  - [x] Make the file executable: `chmod +x scripts/link-skills.sh`

### Update Entrypoint

- [x] **Modify `scripts/entrypoint.sh` to use `link-skills.sh`** — Replace lines 19–31 (the `mkdir -p`, both `for` loops, and the `if [ -d /mnt/skills ]` block) with a single call. Source the helper and call the function:
  ```
  # Step 4: Inject skills
  source /opt/nanobot-nix/scripts/link-skills.sh
  link_skills /opt/nanobot-nix/skills /mnt/skills ~/.nanobot/workspace/skills
  ```
  Verify: The resulting `entrypoint.sh` should no longer contain any `for dir in ... /*/;` loops or `shopt` commands — all glob handling is now in `link-skills.sh`.

## Nix-Install Whitelist Fix

### Extract Whitelist-Checking Logic

- [ ] **Extract `check_package_allowed` function in `scripts/nix-install.sh`** — Refactor `scripts/nix-install.sh` to extract lines 13–33 (the whitelist check block) into a function named `check_package_allowed` that takes a single argument `$1` (the package name) and reads `NANOBOT_NIX_ALLOWED_PACKAGES` from the environment. The function must:
  1. If `NANOBOT_NIX_ALLOWED_PACKAGES` is unset or empty (`[ -z "${NANOBOT_NIX_ALLOWED_PACKAGES:-}" ]`), print `"Nix package installation is disabled (NANOBOT_NIX_ALLOWED_PACKAGES is not set)"` to stderr and `return 1`
  2. If the value equals `"*"` exactly (`[ "$NANOBOT_NIX_ALLOWED_PACKAGES" = "*" ]`), `return 0` (allow all)
  3. Otherwise, split on commas with `IFS=',' read -ra entries <<< "$NANOBOT_NIX_ALLOWED_PACKAGES"`, trim leading/trailing whitespace from each entry using the existing `${entry#...}` / `${entry%...}` pattern substitution, and check if the trimmed entry equals the package name. If found, `return 0`. If loop completes without a match, print `"Package '$1' is not in the allowed list"` to stderr and `return 1`
  - [ ] Update the main body of `nix-install.sh` to call `check_package_allowed "$package"` instead of having the logic inline. The `|| exit 1` after the call handles the non-zero return.
  - [ ] Add a source guard at the top of the function definition section so the file can be sourced for testing without executing the main body. Use the pattern: define the function at the top, then wrap the main execution (argument validation through installation) in `if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then ... fi`

### Investigate Allowed-Packages Env Chain

- [ ] **Verify `NANOBOT_NIX_ALLOWED_PACKAGES` env chain behavior** — Write a test in `tests/test_nix_install.py` (see Shell Script Test Suite group) that specifically validates: when `NANOBOT_NIX_ALLOWED_PACKAGES="*"` is set via `env=` parameter in `subprocess.run`, the `check_package_allowed` function receives the literal string `*` and returns 0 (allow). This confirms the variable survives the env chain without shell expansion. If this test fails, investigate whether the value needs additional quoting or escaping and fix accordingly.

## Shell Script Test Suite

### Link-Skills Tests

- [ ] **Create `tests/test_link_skills.py`** — Create a pytest test file that tests the `link_skills` function from `scripts/link-skills.sh`. Use `subprocess.run` with `bash -c 'source scripts/link-skills.sh && link_skills "$@"' _ <args>` to invoke the function. Use `tmp_path` fixture for temporary directories. Tests to include:
  - [ ] `test_link_builtin_skills` — Create a temp dir with subdirectories `skill_a/` and `skill_b/` as the builtin dir, an empty custom dir, and an empty target dir. Call `link_skills <builtin> <custom> <target>`. Assert that `<target>/skill_a` and `<target>/skill_b` are symlinks pointing to the correct source directories. Assert no `*` entry exists in `<target>/`.
  - [ ] `test_link_custom_skills_override` — Create a builtin dir with `skill_a/`, a custom dir with `skill_a/` (different path), and an empty target dir. Call `link_skills`. Assert that `<target>/skill_a` is a symlink pointing to the custom `skill_a/`, not the builtin one.
  - [ ] `test_link_custom_skills_merged` — Create a builtin dir with `skill_a/`, a custom dir with `skill_b/`, and an empty target. Call `link_skills`. Assert both `skill_a` (pointing to builtin) and `skill_b` (pointing to custom) exist as symlinks in target.
  - [ ] `test_link_no_skills_no_star_directory` — Create empty builtin and custom dirs. Call `link_skills`. Assert `<target>/` is empty (no `*` entry, no files at all). This is the regression test for the `*` directory bug.
  - [ ] `test_link_no_custom_dir` — Create a builtin dir with `skill_a/`, and pass a nonexistent path as the custom dir. Call `link_skills`. Assert `<target>/skill_a` is a symlink and no errors occurred.
  - [ ] `test_link_target_dir_created` — Pass a nonexistent path as the target dir. Call `link_skills`. Assert the target directory was created and contains the expected symlinks.

### Nix-Install Whitelist Tests

- [ ] **Create `tests/test_nix_install.py`** — Create a pytest test file that tests the `check_package_allowed` function from `scripts/nix-install.sh`. Use `subprocess.run` with `bash -c 'source scripts/nix-install.sh && check_package_allowed <pkg>'` to invoke the function, passing `NANOBOT_NIX_ALLOWED_PACKAGES` via the `env=` parameter. Use `capture_output=True, text=True` to capture stdout/stderr. Tests to include:
  - [ ] `test_allowed_packages_unset` — Do not set `NANOBOT_NIX_ALLOWED_PACKAGES` in the env. Call `check_package_allowed "curl"`. Assert return code is 1 and stderr contains `"disabled"`.
  - [ ] `test_allowed_packages_empty_string` — Set `NANOBOT_NIX_ALLOWED_PACKAGES=""`. Call `check_package_allowed "curl"`. Assert return code is 1 and stderr contains `"disabled"`.
  - [ ] `test_allowed_packages_wildcard` — Set `NANOBOT_NIX_ALLOWED_PACKAGES="*"`. Call `check_package_allowed "curl"`. Assert return code is 0 (allowed).
  - [ ] `test_allowed_packages_exact_match` — Set `NANOBOT_NIX_ALLOWED_PACKAGES="curl,wget,jq"`. Call `check_package_allowed "wget"`. Assert return code is 0.
  - [ ] `test_allowed_packages_no_match` — Set `NANOBOT_NIX_ALLOWED_PACKAGES="curl,wget,jq"`. Call `check_package_allowed "vim"`. Assert return code is 1 and stderr contains `"not in the allowed list"`.
  - [ ] `test_allowed_packages_whitespace_trimming` — Set `NANOBOT_NIX_ALLOWED_PACKAGES="curl , wget , jq"`. Call `check_package_allowed "wget"`. Assert return code is 0 (whitespace around entries is trimmed).
  - [ ] `test_allowed_packages_single_entry` — Set `NANOBOT_NIX_ALLOWED_PACKAGES="curl"`. Call `check_package_allowed "curl"`. Assert return code is 0.
  - [ ] `test_allowed_packages_trailing_comma` — Set `NANOBOT_NIX_ALLOWED_PACKAGES="curl,wget,"`. Call `check_package_allowed "wget"`. Assert return code is 0 and no error occurs from the trailing empty entry.

## Docker User/Permissions Documentation

- [ ] **Document Docker user/permissions findings in `CONCERNS.md`** — Add a new section `## Docker User/Permissions` to `.agent/plans/06-testing/CONCERNS.md` documenting:
  1. The container currently runs as root because: Nix requires root (or multi-user daemon setup), the workspace is at `/root/.nanobot/`, and various tools expect root permissions.
  2. When users mount local files (e.g. `./skills:/mnt/skills:ro`), files created by the container are owned by root, which can cause permission conflicts on the host.
  3. Recommended future approach: create a non-root user, configure Nix single-user mode for that user, adjust workspace path to `/home/<user>/.nanobot/`, and use `--user` flag or `USER` directive. This requires its own implementation plan.
  4. Interim mitigation: the `:ro` flag on skill mounts prevents the container from modifying host files, but any files written to bind-mounted writable volumes will still be root-owned.

## Quality & Verification

- [ ] **Run `pre-commit run --all-files`** — After all code changes are complete, run `pre-commit run --all-files` inside the activated virtualenv. Fix any errors or warnings until it passes cleanly. Pay special attention to shellcheck findings on the new/modified shell scripts.
- [ ] **Run `pytest`** — After pre-commit passes, run `pytest` inside the activated virtualenv. All existing tests (27 Python tests) plus the new shell script tests must pass. Resolve any failures before proceeding.
