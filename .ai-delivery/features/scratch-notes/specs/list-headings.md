# Code Spec: List the notes file's headings under the count

- issue: MAX-83
- size: S
- depends_on: MAX-82

This unit extends `scratch_notes.py` so its plain output lists the notes file's
headings, as written, under the `open: N` line. It matters because the developer wants
to see a notes file's structure the moment they switch into a project, without opening
the file.

**Unit:** MAX-83, List the notes file's headings under the count
**Design reference:** `design/1b-contracts.md` "C1: The command", "C2: The functions"
and "The line rules behind `scan_notes`"
**Date:** 2026-10-01

> **Terms used here.** MAX-83 is this unit's Linear issue. MAX-82 is the count unit,
> which creates the two files this unit extends, and MAX-84 is the `--json` unit, which
> follows this one. FR-005 and FR-016 are requirement labels in `requirements.md`. C1
> and C2 are contracts in `design/1b-contracts.md`. *Trailing whitespace* means spaces
> and tabs only.

## Implementation Summary

- **Files to Create:** 0
- **Files to Modify:** 2
  - `scratch_notes.py`
  - `tests/test_scratch_notes.py`
- **Verification to Add:** about 18 test cases in the existing test module
- **Estimated Complexity:** S
- **Requirements covered:** FR-005, FR-016

## Codebase Conventions

As `specs/count-open-items.md` records them, and as the two files now show: standard
library only, postponed annotations, underscored module constants for compiled
patterns, an annotated and documented function for every public name, and tests laid
out as arrange, act, assert. Read both files before changing them and match what is
there.

- **Verification framework:** pytest with no configuration; a plain `uv run pytest`
  from the repository root.
- **Lint, format and types:** `uv run ruff check scratch_notes.py tests/`,
  `uv run ruff format --check scratch_notes.py tests/` and
  `uv run mypy scratch_notes.py tests/`, all clean.

## Technical Context

**Key gotchas:**

- **Extend, don't change.** MAX-82's signatures, errors and tests stay as they are.
  Every existing test must pass without being edited. If one can't, stop and report
  it: that is a contract problem, not something to patch in the test.
- **One pass.** Headings are collected in the same loop that counts open items, so the
  two can never describe different reads of the file.
- **Headings take no indentation.** A line that starts with a space or a tab before
  its `#` is not a heading, although an open item may be indented.
- **Spaces and tabs only.** The character after the `#` marks must be a space, a tab
  or the end of the line, and only trailing spaces and tabs are trimmed. A
  non-breaking space is neither.
- **No new import.** The script still imports only `os`, `re`, `stat` and `sys`, and
  still parses under Python 3.9.

**Reusable utilities:** the test module's loader and its process helper, and the
script's existing fence handling.

**Integration points:**
- MAX-84 puts this unit's headings in the JSON.
- MAX-86, the integration unit, checks that plain and JSON output agree.

## Contract

- **The heading rule** (rule 3 in "The line rules behind `scan_notes`"): outside a
  fence, a line that is not a fence opener or an open item and that starts, with no
  indentation, with one to six `#` followed by a space, a tab or the end of the line.
- **The summary** gains `headings`: an ordered list of text, each heading exactly as
  written, `#` marks included, without its line ending or trailing whitespace.
- **`render_plain`** returns `open: N` and a line feed, then each heading and a line
  feed, in file order. With no headings it returns only the `open: N` line.
- No new failure. No change to the exit codes or to stderr.

## Task Breakdown

### Task 1: Add the heading tests first

**Dependencies:** None (MAX-82 is built)
**Files:** `tests/test_scratch_notes.py` (modify)
**Pattern:** the existing tests in the same file
**Modification note:** `tests/test_scratch_notes.py` — add the heading rule cases after
the existing rule cases for fences, and the heading command case after the existing
command cases.

**Rule cases: what is a heading** (FR-005):
- `# Title`, `## Section` and `###### Deep` are each reported as written.
- `#` followed by a tab and text is a heading.
- `#` alone on a line is a heading, reported as `#`.
- `##` followed only by spaces is a heading, reported as `##`.
- `# Title` followed by trailing spaces and tabs is reported without them.
- `#tag` is not a heading.
- `#######`, seven marks, with or without text after it, is not a heading.
- A title underlined with `===` and one underlined with `---` give no heading.
- ` # indented`, with a leading space, and one with a leading tab, are not headings.
- `#` followed by a non-breaking space and text is not a heading.
- A heading inside a backtick fence and one inside a tilde fence are not headings;
  headings before and after the fence are.
- A heading on line 1 after a UTF-8 byte-order mark is a heading, reported without the
  mark.
- A CRLF copy of a sample gives the same headings as the LF original, with no carriage
  return in any of them.
- Several headings come back in file order.
- A line that is an open item is counted and is not a heading; a heading line does not
  change the open count.

**Rule cases: plain output** (FR-016):
- A summary with a count and two headings renders as `open: N`, then each heading on
  its own line, each ending in a line feed.
- A summary with no headings renders as only the `open: N` line.
- A heading with non-ASCII text is rendered as written.

**Command case:**
- The script run as a process on a file with open items and headings: exit 0, stdout
  is `open: N` followed by the headings in file order, stderr empty.

**Expected state after Task 1:** the new tests fail; every MAX-82 test still passes.

---

### Task 2: Collect the headings and print them

**Dependencies:** Task 1
**Files:** `scratch_notes.py` (modify)
**Modification notes:**
- `scratch_notes.py` — add the heading pattern beside the existing line patterns.
- `scratch_notes.py` — give the summary shape its `headings` field and say so in its
  docstring.
- `scratch_notes.py` — in `scan_notes`, after the open-item test and only outside a
  fence, test the heading rule and collect the line without trailing whitespace.
- `scratch_notes.py` — in `render_plain`, add one line per heading after the count
  line.
**Implementation:** Apply the heading pattern to the whole line, with no nested
repetition. Update the docstrings of `scan_notes`, `render_plain` and the module so
they describe the headings.
**Verification:** every test in the module passes.

---

### Task 3: Quality pass

**Dependencies:** Task 2
**Files:** no new files.
**Implementation:** run, from the repository root:
- `uv run pytest`
- `uv run pytest --cov=scratch_notes --cov-branch --cov-report=term-missing`
- `uv run ruff check scratch_notes.py tests/`
- `uv run ruff format --check scratch_notes.py tests/`
- `uv run mypy scratch_notes.py tests/`
- `uv run bandit -ll scratch_notes.py`

**Verification:** every command exits 0; coverage of the script is at least 80% of
lines and 70% of branches; `git diff --stat` shows changes only in the two files named
above.

## Task Dependency Graph

```
Task 1: heading tests, written first; they fail, MAX-82's tests still pass
    │
    └─→ Task 2: heading pattern, summary field, scan_notes, render_plain
            │
            └─→ Task 3: suite, coverage, ruff, mypy, bandit
```

## Pattern References

- **Verification and code pattern:** `tests/test_scratch_notes.py` and
  `scratch_notes.py` as MAX-82 leaves them — the loader, the process helper, how a rule
  case is laid out, and how a line pattern is declared and applied.

## Implementation Notes

- **Performance:** one more pattern test per line outside a fence, on lines that are
  not open items. No new import and no second pass.
- **Security:** headings are printed as written. Plain mode does not escape control
  characters; `design/1c-operations.md` names this as accepted.
- **Deployment:** none in this unit. Commit nothing.

## Final Verification

**Functionality:**
- [ ] Every acceptance criterion in MAX-83 is met, and FR-005 and FR-016 are each
  covered by at least one test.
- [ ] A file with no headings prints only the `open: N` line.

**Code quality:**
- [ ] No new import; the file still parses under Python 3.9.
- [ ] Clean under ruff check, ruff format, mypy and bandit; docstrings updated.

**Testing:**
- [ ] The heading tests were written first and failed before Task 2.
- [ ] No MAX-82 test was edited, and the whole suite passes.

**Build:**
- [ ] Only `scratch_notes.py` and `tests/test_scratch_notes.py` changed.
