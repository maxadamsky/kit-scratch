# Code Spec: Prove scratch-notes end to end, as the prompt and the developer use it

- issue: MAX-86
- size: S
- depends_on: MAX-82, MAX-83, MAX-84

This unit proves that the finished `scratch_notes.py` holds together: one notes file,
run the way the shell prompt calls it and the way the developer calls it, gives the
same count and the same headings both times, and every failure looks the same in both
modes. It matters because the three units were each tested on their own as they were
built, and nothing yet checks the whole script on one file.

**Unit:** MAX-86, Prove scratch-notes end to end, as the prompt and the developer use it
**Design reference:** `design/1b-contracts.md` "End-to-end testing" and "C3: Failures";
`design/1c-operations.md` "The proof chain" and "Post-deployment checks"
**Date:** 2026-10-01

> **Terms used here.** MAX-86 is this unit's Linear issue, the project's one
> integration issue. MAX-82, MAX-83 and MAX-84 are the count, headings and `--json`
> units it closes. FR-007, FR-009, FR-012 and FR-016 are requirement labels in
> `requirements.md`. C1 and C3 are contracts in `design/1b-contracts.md`. The *prompt*
> is the developer's shell prompt script, outside this repository. The *setup check* is
> the kit's staleness check, which reads FRESH or STALE. The *orchestrator* is the
> main prototype session, which alone writes to Linear.

## Implementation Summary

- **Files to Create:** 0
- **Files to Modify:** 1
  - `tests/test_scratch_notes.py`
- **Verification to Add:** 3 end-to-end tests, one of them run once per failure and
  mode
- **Estimated Complexity:** S

## Shared File Analysis

Every file the feature touches, and which unit touches it:

| File | MAX-82 | MAX-83 | MAX-84 | MAX-86 | Shared? |
|---|---|---|---|---|---|
| `scratch_notes.py` | creates | modifies | modifies | — | **Yes** |
| `tests/test_scratch_notes.py` | creates | modifies | modifies | modifies | **Yes** |

**Resolved conflicts:** none. Nothing was moved into this unit.

**Accepted conflicts (built one after another):**
- `scratch_notes.py` and `tests/test_scratch_notes.py` are shared by all three
  component units. The software profile treats shared files as a defect to restructure.
  Max Adamsky chose one unit per printed output on 2026-10-01 and accepted that the
  units can't be built in parallel (`docs/decisions.md`, 2026-10-01).

**Result:** three batches of one unit each, in the order MAX-82, MAX-83, MAX-84. This
unit runs after all three are verified.

**What integration means here.** The usual integration work is merging shared files and
replacing stand-ins with real implementations. Neither applies: each unit built
directly on the one before, in the same files, with no stand-in. What is left is the
end-to-end proof and the closing checks.

## Codebase Conventions

As the two files now show. Read `tests/test_scratch_notes.py` before changing it and
match what is there: the loader, the process helper, the sample builder, and tests laid
out as arrange, act, assert.

## Technical Context

**Key gotchas:**

- **These tests should pass as soon as they are written.** The script is finished. A
  failure here is a finding about an earlier unit: report it, and do not change
  `scratch_notes.py` or an earlier test to make it pass.
- **Run the script as a process** for all three journeys, with the interpreter running
  the tests. The journeys are about what the prompt and the developer see.
- **Compare the two modes with each other**, not only with expected values. The point
  is that they agree.

**Integration points:** none beyond the script itself. There is no router, registry,
configuration or dependency wiring to merge.

## Task Breakdown

### Task 1: Add the three journeys

**Dependencies:** None (MAX-82, MAX-83 and MAX-84 are verified)
**Files:** `tests/test_scratch_notes.py` (modify)
**Pattern:** the existing command cases in the same file
**Modification note:** `tests/test_scratch_notes.py` — add the three journey tests at
the end of the file, under a comment that names them as the end-to-end journeys.

**Journey 1: the prompt's** (FR-007):
- Write one sample notes file holding headings, open items, done items, a nested open
  item and a fenced block with look-alike lines.
- Run the script on it with `--json`.
- Exit code 0, stderr empty, stdout exactly one line that parses as JSON, and `open`
  is the count the sample was built with.

**Journey 2: the developer's** (FR-016):
- Run the script on the same file without `--json`.
- Exit code 0, stderr empty. The first line is `open: N`, where N equals the JSON
  run's `open`. The remaining lines equal the JSON run's `headings`, in the same
  order.

**Journey 3: failure** (FR-009), run once for each failure below, in plain mode and
with `--json`:
- a missing file
- a directory
- a file one byte over the size limit
- a file that is not valid UTF-8
- a file that ends inside a fence
- no file argument
- an unknown option
- **[REVISED in MAX-86, 2026-10-02]:** a file with all permissions removed; skipped
  with a stated reason when running as the superuser
- **[REVISED in MAX-86, 2026-10-02]:** a named pipe, with the timeout; skipped with a
  stated reason where named pipes can't be created
- **[REVISED in MAX-86, 2026-10-02]:** `/dev/null`; skipped with a stated reason where
  it doesn't exist

**[REVISED in MAX-86, 2026-10-02]:** one more case, run with `--json` only, because the
plain form is already a MAX-82 test: when `/usr/bin/python3` exists and is older than
3.11, the script run with it and `--json` exits non-zero, prints nothing on stdout and
names 3.11 on one stderr line. Skipped with a stated reason otherwise.

For each: stdout is empty, stderr is exactly one line that starts with
`scratch_notes: `, and the exit code is 2 for the two command-line failures and 1 for
the rest.

**Expected state after Task 1:** the three journeys pass, and every earlier test still
passes unchanged.

---

### Task 2: Quality pass

**Dependencies:** Task 1
**Files:** no new files.
**Implementation:** run, from the repository root:
- `uv run pytest`
- `uv run pytest -s -k timing`, and keep the `timings_ms:` line for the hand-back
- `uv run pytest --cov=scratch_notes --cov-branch --cov-report=term-missing`
- `uv run ruff check scratch_notes.py tests/`
- `uv run ruff format --check scratch_notes.py tests/`
- `uv run mypy scratch_notes.py tests/`
- `uv run bandit -ll scratch_notes.py`

**Verification:** every command exits 0; coverage of the script is at least 80% of
lines and 70% of branches; `git diff --stat` shows this unit changed only the test
file.

---

### Task 3: Closing checks, run by the orchestrator

**Dependencies:** Task 2
**Files:** none.
**Implementation:** these steps write to Linear or read the kit's own record, so the
orchestrator does them, not an implementer:
- Run the setup check and confirm it reads FRESH.
- Run `gitleaks detect --source .` and `uv run pip-audit`, the recorded
  secret-detection and dependency gates.
- Post the 20 timings, with the slowest, as a comment on MAX-86.
- Confirm `git status --short` shows only `scratch_notes.py`, `tests/` and files under
  `.ai-delivery/` and `docs/` as changed.

**Verification:** the setup check reads FRESH; both scans are clean; the slowest timing
is under 50 ms.

## Task Dependency Graph

```
Task 1: three journeys added; they pass on the finished script
    │
    └─→ Task 2: suite, timings, coverage, ruff, mypy, bandit
            │
            └─→ Task 3 (orchestrator): setup check, gitleaks, pip-audit, timings to Linear
```

## Pattern References

- **Verification pattern:** the command cases in `tests/test_scratch_notes.py` — the
  process helper, how a sample file is written to pytest's temporary directory, and how
  stdout, stderr and the exit code are asserted.

## Implementation Notes

- **Performance:** the journeys add a few dozen short processes to the suite.
- **Security:** the journeys read only files they create in pytest's temporary
  directory.
- **Deployment:** none. Commit nothing; Max Adamsky commits and opens the pull request
  at handoff.
- **What this unit does not prove:** that the count equals a hand count on real notes
  files. No real notes files exist here. Max Adamsky owns that check, after the
  prototype.

## Revision History

| Date | Change | Reason | Rework ID |
|------|--------|--------|-----------|
| 2026-10-02 | The failure journey gains an unreadable file, a named pipe and `/dev/null` in both modes, and the old-Python run with `--json`. | The verifier of MAX-84 found these four failures tested in plain mode only. The design gives "each failure in C3, in both modes" to integration, so the cases belong here. A Targeted addition to this spec's test list, with no change to the script. | MAX-86 |

## Final Verification

**Functionality:**
- [ ] Every acceptance criterion in MAX-86 is met.
- [ ] Plain and JSON output agree on the count and the headings for the same file.
- [ ] Every failure, in both modes, leaves stdout empty, puts one line on stderr and
  exits non-zero.

**Code quality:**
- [ ] The test file is clean under ruff check, ruff format and mypy.
- [ ] `scratch_notes.py` is unchanged by this unit.

**Testing:**
- [ ] `uv run pytest` passes with every earlier test unchanged.
- [ ] Coverage of the script is at least 80% of lines and 70% of branches.
- [ ] The 20 timings are recorded on MAX-86, and the slowest is under 50 ms.

**Build:**
- [ ] The setup check reads FRESH.
- [ ] gitleaks and pip-audit are clean.
