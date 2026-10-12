# Code Spec: Give the shell prompt the count and headings as JSON

- issue: MAX-100
- size: M
- depends_on: MAX-98, MAX-99

This unit adds a `--json` option to `scratch_notes.py`, so the developer's shell prompt
can read the open count and the headings from one line on every draw. It matters
because showing that count in the prompt is the reason the tool exists, and the prompt
needs an answer in under 50 ms.

**Unit:** MAX-100, Give the shell prompt the count and headings as JSON
**Design reference:** `design/1b-contracts.md` "C1: The command", "C2: The functions",
"C3: Failures" and "Testing strategy"; `design/1c-operations.md` "Performance and
scalability"
**Date:** 2026-10-01

> **Terms used here.** MAX-100 is this unit's Linear issue. MAX-98 and MAX-99 are the
> count and headings units, which this one extends. FR-007, FR-012 and FR-017 are
> requirement labels in `requirements.md`. C1 to C3 are contracts in
> `design/1b-contracts.md`. The *prompt* is the developer's shell prompt script, outside
> this repository. The *size limit* is 1,048,576 bytes, the largest file the script
> accepts.

## Implementation Summary

- **Files to Create:** 0
- **Files to Modify:** 2
  - `scratch_notes.py`
  - `tests/test_scratch_notes.py`
- **Verification to Add:** about 20 test cases in the existing test module, including
  one timing test, plus one sample builder
- **Estimated Complexity:** M
- **Requirements covered:** FR-007, FR-012

## Codebase Conventions

As `specs/count-open-items.md` records them, and as the two files now show. Read both
files before changing them and match what is there.

- **Imports:** this unit adds `json` to the script's imports, in the place ruff's
  default sorting puts it. No other import is added.
- **Verification framework:** pytest with no configuration; a plain `uv run pytest`
  from the repository root.
- **Lint, format and types:** `uv run ruff check scratch_notes.py tests/`,
  `uv run ruff format --check scratch_notes.py tests/` and
  `uv run mypy scratch_notes.py tests/`, all clean.

## Technical Context

**Key gotchas:**

- **Extend, don't change.** Every MAX-98 and MAX-99 test must pass without being
  edited. Those tests were written so `--json` could become valid and the usage text
  could grow. If one fails, stop and report it.
- **The JSON text is fixed, character for character.** The key `open` comes first,
  then `headings`. The separators are the encoder's defaults: a comma and a space, a
  colon and a space. Characters outside ASCII are written as `\u` escapes, also the
  default. Do not pass options that change any of this.
- **`open` is a JSON number**, never text.
- **A failure with `--json` is still a failure.** Stdout stays empty: no JSON error
  object is ever printed. The prompt tells success from failure by the exit code.
- **The timing test names one interpreter.** FR-012 is a promise about the prompt's
  interpreter, `/opt/homebrew/bin/python3`, not about the interpreter running the
  tests. Where that path doesn't exist, the test is skipped with a stated reason.
- **The file still parses under Python 3.9.**

**Reusable utilities:** the test module's loader and its process helper; the script's
`scan_notes`, which already returns the count and the headings.

**Integration points:**
- The prompt reads this unit's output.
- MAX-102, the integration unit, checks that plain and JSON output agree, and records
  the timings this unit's timing test prints.

## Contract

- **`parse_arguments`** accepts `--json` once, before or after the path. A second
  `--json` is a `UsageError` with the reason `option --json given twice`. Every other
  option is still unknown. The request gains `as_json`, true when the option is given.
- **The usage text** becomes `usage: scratch_notes.py <file> [--json] (<reason>)`.
- **`render_json`** takes a summary and returns one line: a JSON object with exactly
  the keys `open` and `headings`, in that order, then a line feed.
- **`run`** renders with `render_json` when the request asks for JSON, and with
  `render_plain` otherwise. Its order of work and its handling of failures are
  unchanged.
- **Exact output for a small file.** A file holding `# Plan`, an open item, a done
  item and `## Later` gives `{"open": 1, "headings": ["# Plan", "## Later"]}`.
- **An empty file** gives `{"open": 0, "headings": []}`.
- **Time:** each call finishes within 50 ms on the sample builder's notes-like file at
  the size limit (FR-012, revised 2026-10-02). Files of very short lines may take
  longer; that is accepted and is not this unit's to fix.

## Task Breakdown

### Task 1: Add the JSON tests and the sample builder first

**Dependencies:** None (MAX-98 and MAX-99 are built)
**Files:** `tests/test_scratch_notes.py` (modify)
**Pattern:** the existing tests in the same file
**Modification notes:**
- `tests/test_scratch_notes.py` — add the sample builder beside the existing helpers.
- `tests/test_scratch_notes.py` — add the JSON rule cases after the heading rule
  cases, and the JSON command cases and the timing test after the existing command
  cases.

**The sample builder.** A helper that takes a size in bytes and returns three things:
notes text of exactly that many bytes, the open count that text holds, and its headings
in order. It builds the text from repeating blocks, each holding a heading, prose, an
open item, a done item, a nested open item, and a fenced block holding a look-alike
open item and a look-alike heading. It pads the last line so the size is exact. The
count and headings are known from how the text was built, not by running the script.

**Rule cases: arguments** (FR-007):
- A path then `--json`, and `--json` then a path, both give a request for JSON with
  that path.
- A path alone gives a request for plain text.
- `--json` twice raises `UsageError` naming the repeated option.
- `--json` with no path, and with two paths, raise `UsageError` naming the count.
- `--verbose` is still a `UsageError`, and a usage message now holds `[--json]`.

**Rule cases: `render_json`** (FR-007):
- The small file in the contract gives exactly the text shown there, with a line feed.
- A summary with no headings and a count of 0 gives `{"open": 0, "headings": []}`.
- The output is one line: it holds exactly one line feed, at the end.
- Parsing the output gives an object with exactly the keys `open` and `headings`,
  where `open` is a whole number and not a boolean or text, and `headings` is a list
  of text.
- A heading holding a double quote, a backslash and non-ASCII text parses back to the
  heading as written, and the output itself is pure ASCII.

**Rule cases: `run` with `--json`:**
- A good file returns exit code 0, the JSON line as stdout and empty stderr.
- Each failure returns the exit code C3 names, empty stdout and one stderr line.
  Cover: missing file, directory, oversized file, invalid UTF-8 and unclosed fence.
- The sample builder's text at the size limit, written to a file, gives exactly the
  count and headings the builder returned.

**Command cases:**
- The script run as a process with `--json` on a small file: exit 0, the exact JSON
  line, stderr empty.
- The same with the interpreter flags `-I -S`: the same result.
- An unclosed fence with `--json`: exit 1, stdout empty, one stderr line.

**The timing test** (FR-012):
- Skip with a stated reason unless `/opt/homebrew/bin/python3` exists.
- Write the builder's sample at the size limit to pytest's temporary directory.
- Run `/opt/homebrew/bin/python3 scratch_notes.py <sample> --json` 20 times in a row,
  timing each run end to end.
- Print the 20 timings in milliseconds on one line that starts with `timings_ms:`, so
  verification can record them.
- Assert that every run exited 0 and that the slowest took under 50 ms, with the
  timings in the failure message.

**Expected state after Task 1:** the new tests fail; every earlier test still passes.

---

### Task 2: Accept `--json`

**Dependencies:** Task 1
**Files:** `scratch_notes.py` (modify)
**Modification notes:**
- `scratch_notes.py` — give the request shape its `as_json` field and say so in its
  docstring.
- `scratch_notes.py` — in `parse_arguments`, accept `--json` once in either position,
  and add `[--json]` to the usage text.
**Implementation:** Keep the order of checks: an unknown option is reported first, then
a repeated `--json`, then a wrong path count.
**Verification:** the argument rule cases pass.

---

### Task 3: `render_json` and the choice of renderer

**Dependencies:** Task 2
**Files:** `scratch_notes.py` (modify)
**Modification notes:**
- `scratch_notes.py` — add `json` to the imports.
- `scratch_notes.py` — add `render_json` after `render_plain`.
- `scratch_notes.py` — in `run`, choose the renderer from the request.
**Implementation:** Build the object with `open` first and `headings` second and
encode it with the standard encoder's defaults. Update the module docstring so it
shows both ways of running the script.
**Verification:** every test in the module passes, including the timing test on this
machine.

---

### Task 4: Quality pass

**Dependencies:** Task 3
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
lines and 70% of branches; the slowest of the 20 timings is under 50 ms;
`git diff --stat` shows changes only in the two files named above.

## Task Dependency Graph

```
Task 1: JSON tests, sample builder and timing test, written first; they fail
    │
    └─→ Task 2: --json in parse_arguments, the request's as_json, the usage text
            │
            └─→ Task 3: render_json, the renderer choice in run
                    │
                    └─→ Task 4: suite, timings, coverage, ruff, mypy, bandit
```

## Pattern References

- **Verification and code pattern:** `tests/test_scratch_notes.py` and
  `scratch_notes.py` as MAX-99 leaves them — the loader, the process helper, how
  `parse_arguments` sorts options from paths, and how `render_plain` and `run` are
  written.

## Implementation Notes

- **Performance:** `json` adds about 1 ms of start-up (`design/1a-discovery.md`). The
  real script took 27 to 33 ms on a notes-like 1 MiB sample before headings and JSON
  were added (`design/1c-operations.md`), so expect about 10 ms to spare. If the timing
  test fails, report the timings; do not raise the limit or shrink the sample.
- **Security:** the encoder escapes quotes, backslashes, control characters and
  everything outside ASCII, so a heading can't break the line the prompt reads.
- **Deployment:** none in this unit. Commit nothing. Pointing the prompt at the script
  is Max Adamsky's step, outside this repository.
- **Rubric note:** the timing test names a fixed interpreter path. That is the
  requirement's own wording, not a stand-in: FR-012 is timed with the interpreter the
  prompt uses.

## Revision History

| Date | Change | Reason | Rework ID |
|------|--------|--------|-----------|
| 2026-10-02 | The 50 ms limit is promised for a notes-like file at the size limit, not for every file the script accepts. | Timing the real script at 1 MiB took at most 33 ms on a notes-like mix, 47 ms with an open item on every line and 165 ms on empty lines only: the time follows the number of lines. Max Adamsky kept the 1 MiB limit and restated the promise. | MAX-100 |

## Final Verification

**Functionality:**
- [ ] Every acceptance criterion in MAX-100 and its Prototype notes is met, and FR-007
  and FR-012 are each covered by at least one test.
- [ ] Every failure with `--json` leaves stdout empty and exits non-zero.

**Code quality:**
- [ ] `json` is the only new import; the file still parses under Python 3.9.
- [ ] Clean under ruff check, ruff format, mypy and bandit; docstrings updated.

**Testing:**
- [ ] The JSON tests were written first and failed before Task 2.
- [ ] No earlier test was edited, and the whole suite passes.
- [ ] The 20 timings are in the hand-back, and the slowest is under 50 ms.

**Build:**
- [ ] Only `scratch_notes.py` and `tests/test_scratch_notes.py` changed.
