# Code Spec: Integrate the pull request checklist with its README link

- issue: MAX-47
- size: S
- depends_on: MAX-45, MAX-46

This unit joins the two separately built units into one working feature. It proves that
the README's last link opens the checklist, and it returns the kit's setup check to
FRESH after the README edit. It matters because each unit was checked in isolation, and
until setup re-runs, every kit skill stops at the setup check.

**Unit:** MAX-47, Integrate the pull request checklist with its README link
**Design reference:** `design/1b-contracts.md` "Contract C3: the setup record",
"Contract C4: the acceptance checks" and "Testing strategy"; `design/1c-operations.md`
"Deployment strategy"
**Date:** 2026-09-22

> **Terms used here.** MAX-45 (`CONTRIBUTING.md`), MAX-46 (the README sentence) and MAX-47
> (this unit) are Linear issues. C1 to C4 are contracts in `design/1b-contracts.md`. The
> *setup check* is the kit's staleness check, which reads FRESH or STALE. The *setup
> record* is `.ai-delivery/stack-fingerprint`. The *main session* is the orchestrating
> session, as opposed to a subagent; the kit's write guard refuses a subagent's write to
> setup's files.

## Implementation Summary

- **Files to Create:** 1
  - `.ai-delivery/features/pull-request-checklist/checks/test_checklist_reachable.py`
- **Files to Modify:** 1 or more, all by the setup re-run in the main session:
  - `.ai-delivery/stack-fingerprint`, for README's new hash
  - whichever of `.ai-delivery/config.md`, `.ai-delivery/conventions.md` and
    `docs/decisions.md` the re-run rewrites
- **Verification to Add:** 1 test module, about 6 test functions: 3 against the real
  files and 3 against temporary sample files
- **Estimated Complexity:** S. Integration complexity is one shared file, the setup
  record.
- **Implemented by:** the orchestrator directly, because the setup re-run can only run
  in the main session.

## Codebase Conventions

The conventions are the same as the two unit specs'. The module is `test_checklist_reachable.py`,
uses the standard library and pytest's own `tmp_path` fixture only, and carries a module
docstring and a docstring on every function. It must be clean under ruff check, ruff
format and mypy. Run it from the repository root:
`PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider --import-mode=importlib .ai-delivery/features/pull-request-checklist/checks/test_checklist_reachable.py`

## Technical Context

**Key gotchas:**
- **Setup owns the setup record.** The record is written only through a setup re-run in
  the main session, never by hand and never by a subagent.
- **The re-run may touch more than the record.** A setup re-run after a hash change runs
  full detection and may rewrite `conventions.md`, `config.md` dates and
  `docs/decisions.md`. Capture `git status --short` before and after, list every file it
  changes, and report any change beyond README's hash and those records to Max Adamsky
  rather than accepting it silently.
- **The re-run may ask questions.** Setup asks when it proposes a change to an existing
  artifact. Those questions are Max Adamsky's to answer.
- **Path safety.** The link target comes from README text, so resolve it inside the
  repository root and refuse any target that escapes it, such as `../CONTRIBUTING.md`.
- **No shared helper.** Do not import from the two unit modules. Re-parse what this
  module needs, so that no module depends on another.

**Integration points:**
- It consumes C2, README's last link, and C1, the checklist's title and five items.
- It resolves C3: after the re-run, the setup check reads FRESH.

## Shared File Analysis

**Resolved conflicts:** none were needed. MAX-45 and MAX-46 touch disjoint files. The
checks directory holds one module per unit and no shared `__init__.py`, `conftest.py` or
helper module.

**Accepted shared files:** `.ai-delivery/stack-fingerprint`, and setup's other records
the re-run touches. Only the setup re-run in the main session writes them, at
integration.

**Result:** MAX-45 and MAX-46 share the first batch. This unit runs after both are
verified.

## Task Breakdown

### Task 1: Write the integration check module first

**Dependencies:** MAX-45 and MAX-46 verified
**Files:** `.ai-delivery/features/pull-request-checklist/checks/test_checklist_reachable.py`
(create)
**Pattern:** the two unit modules, for structure, root resolution and failure-message
style.
**Implementation:**
- Parse README's last paragraph and take its single link target.
- Resolve the target against the repository root. Require that it stays inside the root
  and names a regular file.
- Read that file, and confirm it begins with a level-1 heading and holds exactly five
  numbered items.
- Keep the resolution in a pure function that takes a root directory and README text, so
  that the adverse cases can run against a temporary root.

**Cases against the real files:**
- README's link target resolves to a regular file inside the root → UnresolvedLink.
- The resolved file is the root's `CONTRIBUTING.md` → UnresolvedLink.
- That file begins with a level-1 heading and holds exactly five numbered items →
  UnresolvedLink, noting that the target does not hold the checklist.

**Adverse cases** (pytest's `tmp_path`, one fresh directory per test):
- A root with the README sample and no target file is reported as UnresolvedLink.
- A README sample whose target is `../CONTRIBUTING.md` is reported as UnresolvedLink,
  refused because the target escapes the root.
- A target file with four items is reported as UnresolvedLink.

**Expected state after Task 1:** the module passes, because both units' files exist. The
setup check still reads STALE, which is recorded as the before-state for Task 2.

---

### Task 2: Re-run setup and confirm the setup check reads FRESH

**Dependencies:** Task 1
**Files:** `.ai-delivery/stack-fingerprint` and whichever records the re-run rewrites.
The main session makes these changes, through setup only.
**Implementation:**
1. Run the setup check and record its STALE output: the status plus its stderr lines.
2. Capture `git status --short`.
3. Run the setup skill as a re-run in this session. Max Adamsky answers any question it
   asks.
4. Capture `git status --short` again, and diff every file the re-run changed.
5. Run the setup check again, which must print FRESH and exit 0.

**Verification:**
- The setup check prints FRESH.
- Every file the re-run changed is listed, with a one-line reason each.
- Nothing outside setup's records changed.

---

### Task 3: Integration evidence and quality pass

**Dependencies:** Task 2
**Files:** no new files.
**Implementation:** run, from the repository root:
- the whole checks directory:
  `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider --import-mode=importlib .ai-delivery/features/pull-request-checklist/checks/`
- a plain `uv run pytest`, which must print "no tests ran" and exit with code 5
- `git diff 7133948 -- README.md`, which must show only added lines at the end
- `uv run ruff check`, `uv run ruff format --check` and `uv run mypy`, each on the checks
  directory
- `uv run bandit -r .ai-delivery/features/pull-request-checklist/checks/ -ll`
- gitleaks over the new and changed files
- the recorded gates in `.ai-delivery/gates.md` exactly as written. Their `src/` and
  `tests/` failures are the known pre-existing gap recorded in `design/1c-operations.md`,
  not a regression.

**Verification:**
- Every check module passes.
- The plain run exits with code 5.
- The README diff is additions only.
- ruff, mypy and bandit are clean on the checks directory.
- gitleaks finds nothing.

## Task Dependency Graph

```
MAX-45 verified ─┐
                 ├─→ Task 1: integration check module; it passes, and the setup check is STALE
MAX-46 verified ─┘       │
                         └─→ Task 2: setup re-run; the setup check reads FRESH
                                 │
                                 └─→ Task 3: full checks run, plain pytest exits 5,
                                     README diff, ruff, mypy, bandit, gitleaks
```

## Pattern References

- **Verification pattern:** `test_contributing.py` and `test_readme_link.py` from
  MAX-45 and MAX-46, for root resolution, pure parsing functions and failure messages
  that name their condition.

## Implementation Notes

- **Security:**
  - Path traversal through the link target is refused.
  - No network, subprocess or git calls are made from the module; the git and gitleaks
    runs are evidence commands.
- **Deployment:** nothing is committed or pushed. The route to `main` is question 3, at
  handoff.
- **Close-out after post-integration verification passes:**
  - Move MAX-45, MAX-46 and MAX-47 to Done.
  - Post a closing comment on MAX-47 listing the shared files merged, the cross-unit
    wiring verified, the check results, and the suite and linter status.

## Final Verification

**Functionality:**
- [ ] README's last link resolves to the root `CONTRIBUTING.md`, which holds the
  checklist.
- [ ] The setup check reads FRESH after the re-run.
- [ ] A plain `uv run pytest` still prints "no tests ran" and exits with code 5.

**Code quality:**
- [ ] The module is clean under ruff check, ruff format, mypy and bandit, and is fully
  annotated and documented.

**Testing:**
- [ ] All three check modules pass together.
- [ ] The adverse cases prove that the resolver can fail.

**Build:**
- [ ] The only changes beyond the two units' files are this module and setup's records.
- [ ] Each change the re-run made is listed with its reason.
