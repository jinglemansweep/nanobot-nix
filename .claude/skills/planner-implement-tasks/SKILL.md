# planner-implement-tasks

Implement tasks from a task list, one at a time, with strict quality gates between each.

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

## Instructions

### Step 1: Read the Task List

Read `<plan-dir>/TASKS.md`. If missing, stop and tell the user to run `planner-create-tasklist` first.

### Step 2: Find the Next Incomplete Task

Scan `TASKS.md` for the first unchecked task (`- [ ]`). This is the current task. If all tasks are checked (`- [x]`), report that all tasks are complete and stop.

### Step 3: Implement the Current Task

Implement exactly what the task describes. The task description in `TASKS.md` is the sole source of truth — do not reference `PLAN.md`, `RESEARCH.md`, or any other planning file.

- If the task has subtasks, implement all subtasks before considering the parent task complete.
- If a task is unclear or impossible to implement as described, stop and ask the user for clarification. Do not guess or improvise.
- Do not implement beyond the current task. Do not look ahead or pre-build for future tasks.

### Step 4: Quality Gates

After implementing the task, run **all** applicable quality checks:

1. **Linting** — run the project's configured linter(s). Fix all errors and warnings.
2. **Type checking** — run type checkers if configured. Fix all errors.
3. **Tests** — run the project's test suite. Fix all failures.
4. **Build** — run the build if applicable. Fix all errors.

Detect which tools are available by checking project config files (`package.json`, `pyproject.toml`, `Makefile`, `.github/workflows/`, etc.) and use whatever is configured.

**ALL errors and warnings must be resolved before proceeding.** If a quality gate fails:
1. Fix the issue.
2. Re-run **all** quality gates from the beginning (not just the one that failed).
3. Repeat until every gate passes cleanly.

### Step 5: Update TASKS.md

Once all quality gates pass, update `<plan-dir>/TASKS.md`:
- Mark the completed task and all its subtasks as done: `- [ ]` → `- [x]`
- Do not modify any other tasks.

### Step 6: Git Commit

Create a git commit (do NOT push) with all changes from this task. The commit message should follow the format:

```
<type>: <concise description of what was implemented>

Task: <task title from TASKS.md>
Plan: <plan-dir>
```

Where `<type>` is one of: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`.

### Step 7: Stop

**STOP.** Report to the user:
- Which task was completed
- Summary of what was implemented
- Quality gate results (all passing)
- The git commit that was created
- How many tasks remain

Then prompt the user to clear context before continuing:

> Context should be cleared before the next task. Run `/clear` then re-invoke `/planner-implement-tasks <plan-dir>` to continue.

**Do NOT proceed to the next task.** Each task runs in a fresh context to avoid accumulated context degradation.

## Guidelines

- **One task per invocation.** Never implement more than one top-level task (and its subtasks) per run.
- **TASKS.md is the only input.** Do not read or reference planning files. Everything needed is in the task description.
- **Zero tolerance on quality gates.** No warnings, no skipped tests, no "will fix later". Every gate must pass before the task is considered complete.
- **Do not refactor or improve code beyond the task.** If you notice issues in unrelated code, leave them — they may be addressed by a future task.
- **Do not skip tasks.** Tasks are ordered intentionally. Implement them in sequence.
- **Commit granularity = one task.** Each commit corresponds to exactly one completed task.
