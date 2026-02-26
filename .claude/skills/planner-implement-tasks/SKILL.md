# planner-implement-tasks

Implement tasks from a task list, grouped by section, with quality gates and commits per group.

## Usage

```
/planner-implement-tasks <plan-dir>
```

**Argument:**
- `<plan-dir>` — Path to the plan directory (e.g. `.agent/plans/01-initial`). This directory must contain `TASKS.md`.

**Directory convention:**

```
<plan-dir>/
├── PROMPT.md       ← original requirements (not read by this skill)
├── RESEARCH.md     ← research findings (not read by this skill)
├── PLAN.md         ← implementation plan (not read by this skill)
├── CONCERNS.md     ← concerns and risks (not read by this skill)
└── TASKS.md        ← task list (input — the ONLY file this skill reads)
```

## Task Grouping

Tasks in `TASKS.md` are organized under markdown headings (e.g., `## Deletions — Remove Mapping Layer`). Each heading defines a **group** — a logical unit of work. All tasks under a heading belong to the same group. Quality gates and git commits happen once per group, not per task.

## Instructions

### Step 1: Read the Task List

Read `<plan-dir>/TASKS.md`. If missing, stop and tell the user to run `planner-create-tasklist` first.

### Step 2: Find the Next Incomplete Group

Scan `TASKS.md` for the first group (heading section) that contains at least one unchecked task (`- [ ]`). This is the current group. If all tasks across all groups are checked (`- [x]`), report that all tasks are complete and stop.

### Step 3: Implement All Tasks in the Current Group

Implement every unchecked task in the current group, in order. The task descriptions in `TASKS.md` are the sole source of truth — do not reference `PLAN.md`, `RESEARCH.md`, or any other planning file.

- If a task has subtasks, implement all subtasks before considering the parent task complete.
- If a task is unclear or impossible to implement as described, stop and ask the user for clarification. Do not guess or improvise.
- Do not implement tasks from other groups. Only work within the current group.
- Mark each task as done (`- [x]`) in `TASKS.md` as you complete it within the group.

### Step 4: Quality Gates (After the Group)

After all tasks in the group are implemented, run **all** applicable quality checks:

1. **Linting** — run the project's configured linter(s). Fix all errors and warnings.
2. **Type checking** — run type checkers if configured. Fix all errors.
3. **Tests** — run the project's test suite. Fix all failures.
4. **Build** — run the build if applicable. Fix all errors.

Detect which tools are available by checking project config files (`package.json`, `pyproject.toml`, `Makefile`, `.github/workflows/`, etc.) and use whatever is configured.

**ALL errors and warnings must be resolved before proceeding.** If a quality gate fails:
1. Fix the issue.
2. Re-run **all** quality gates from the beginning (not just the one that failed).
3. Repeat until every gate passes cleanly.

### Step 5: Git Commit (After the Group)

Create a single git commit (do NOT push) with all changes from the group. The commit message should follow the format:

```
<type>: <concise description of what was implemented>

Group: <group heading from TASKS.md>
Plan: <plan-dir>
```

Where `<type>` is one of: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`.

### Step 6: Stop

**STOP.** Report to the user:
- Which group was completed
- Summary of tasks implemented
- Quality gate results (all passing)
- The git commit that was created
- How many groups remain

Then prompt the user to clear context before continuing:

> Context should be cleared before the next group. Run `/clear` then re-invoke `/planner-implement-tasks <plan-dir>` to continue.

**Do NOT proceed to the next group.** Each group runs in a fresh context to avoid accumulated context degradation.

## Guidelines

- **One group per invocation.** Never implement more than one group (heading section) per run. Implement all tasks within that group before stopping.
- **TASKS.md is the only input.** Do not read or reference planning files. Everything needed is in the task description.
- **Zero tolerance on quality gates.** No warnings, no skipped tests, no "will fix later". Every gate must pass before the group is considered complete.
- **Do not refactor or improve code beyond the tasks.** If you notice issues in unrelated code, leave them — they may be addressed by a future task.
- **Do not skip tasks or groups.** Tasks and groups are ordered intentionally. Implement them in sequence.
- **Commit granularity = one group.** Each commit corresponds to one completed group of tasks.
