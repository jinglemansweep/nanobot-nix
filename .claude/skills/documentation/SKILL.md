# Documentation Audit

Audit all project documentation for accuracy and completeness, cross-referencing against the actual codebase.

## Usage

```
/documentation
```

## Instructions

### Step 1: Inventory

List all documentation files in the project:

- `README.md`
- `CLAUDE.md`
- `.env.example`
- All `SKILL.md` files under `.claude/skills/`
- Significant inline documentation (Python docstrings, shell script comments)

Use `Glob` and `Read` tools to locate and read each file.

### Step 2: Cross-Reference Code

For each documentation file, verify the following against the actual codebase:

- **Environment variables** — All environment variable names mentioned must match keys in `scripts/config_schema.py`'s `ENV_MAP` and `ALIASES`. Use `Grep` and `Read` to check.
- **File paths and directories** — All file paths, directory references, and command examples must actually exist and work. Use `Glob` to verify paths.
- **Build arguments and Docker config** — All build arguments, Docker image names, and port numbers must match `Dockerfile` and `docker-compose.yml`. Use `Read` to compare.
- **Feature descriptions** — Feature descriptions must match actual code behavior. Read the relevant source code to verify.

### Step 3: Identify Gaps

Check for:

- Features present in code but missing from documentation.
- Deprecated or removed features still mentioned in documentation.
- Inconsistencies between different documentation files (e.g., `README.md` says one thing, `.env.example` says another).

### Step 4: Report and Fix

Produce a summary of findings organized as:

- **Accurate items** — Documentation that correctly reflects the codebase.
- **Stale items** — Documentation that references removed or changed features.
- **Missing items** — Features or configuration present in code but not documented.

Apply fixes directly to the documentation files using the `Edit` tool. For each fix, explain what was changed and why.
