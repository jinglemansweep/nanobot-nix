# Concerns

> Source: `.agent/plans/02-initial-fixes/PROMPT.md`

## Open Questions

- No open questions. All four items in the prompt are well-defined.

## Potential Blockers

- [RESOLVED] The `config_generate.py` import style (`from config_schema import ...`) assumes the script runs from its own directory. If the import path setup in `conftest.py` is fragile, tests may break when run from different working directories. → **Decision:** Make `scripts/` a proper Python package with `__init__.py`. Use `python -m scripts.config_generate` for invocation. Internal imports become relative (e.g., `from .config_schema import ...`). Tests import directly via `from scripts.config_schema import ...`. This eliminates the need for `conftest.py` sys.path hacks.
- [RESOLVED] The Dockerfile currently has no `WORKDIR` set. The `python -m scripts.config_generate` invocation requires that the working directory (or `PYTHONPATH`) includes the parent of `scripts/`. → **Decision:** Add `WORKDIR /opt/nanobot-nix` to the Dockerfile before the ENTRYPOINT. The entrypoint.sh script can drop its `cd` command since WORKDIR handles it. This is the cleanest Docker convention.

## Risks

- [RESOLVED] Shellcheck may surface warnings in the existing shell scripts that require non-trivial refactoring. The `nix-install.sh` script uses `echo "$entry" | xargs` for trimming whitespace (line 23), which shellcheck may flag. → **Decision:** Fix all warnings. No `# shellcheck disable=` suppressions. The scripts are small enough that all patterns can be rewritten cleanly.
- [RESOLVED] The documentation skill's effectiveness depends entirely on the quality of its SKILL.md prompt. It may need iteration after initial use to tune its thoroughness vs. false-positive rate. → **Decision:** Accepted as inherent. Scope confirmed as all documentation files plus inline comments (README.md, CLAUDE.md, .env.example, SKILL.md files, Python docstrings, shell script comments). Iteration expected.

## Future Considerations

- [RESOLVED] The `tests/` directory currently has no CI integration. A future task should add a GitHub Actions job that runs `pytest` and `pre-commit` on PRs. → **Decision:** Add CI now as part of this plan. A lightweight GitHub Actions workflow running pytest and pre-commit on PRs.
- [RESOLVED] As the project grows, the documentation skill may need to be scoped more precisely (e.g., excluding generated files or third-party content) to avoid noise. → **Decision:** Full scope confirmed for now (all docs + inline comments). Will revisit if noise becomes an issue.
- [RESOLVED] Consider adding a `pyproject.toml` or `requirements-dev.txt` to formalize dev dependencies (pytest, pre-commit, shellcheck) for contributors. → **Decision:** Add `pyproject.toml` with `[project.optional-dependencies]` dev section. Enables `pip install -e .[dev]` for contributors.
