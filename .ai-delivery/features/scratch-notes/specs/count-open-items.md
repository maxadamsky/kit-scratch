# Code Spec: Count the open checklist items in a notes file

- issue: MAX-98
- size: L
- depends_on: NONE (first unit; the other two units wait for it)

This unit creates `scratch_notes.py` at the repository root and its test file, so that
`python3 scratch_notes.py <file>` prints `open: N`, a count of open checklist items the
developer can trust. It matters because the grep used today miscounts them, and because
the headings and `--json` units both build on what this unit lays down.

**Unit:** MAX-98, Count the open checklist items in a notes file
**Design reference:** `design/1b-contracts.md` "C1: The command", "C2: The functions",
"The line rules behind `scan_notes`", "C3: Failures" and "C4: The tests";
`design/1a-discovery.md` "ADR-001" and "ADR-002"
**Date:** 2026-10-01

> **Terms used here.** MAX-98 is this unit's Linear issue. MAX-99 and MAX-100 are the
> headings and `--json` units that extend the same two files after this one. FR-001 to
> FR-017 are requirement labels in `requirements.md`. C1 to C4 are the contracts in
> `design/1b-contracts.md`. ADR-001 and ADR-002 are the decision records in
> `design/1a-discovery.md`. The *prompt* is the developer's shell prompt script, outside
> this repository. *Indentation* and *trailing whitespace* mean spaces and tabs only.

## Implementation Summary

- **Files to Create:** 2
  - `scratch_notes.py`
  - `tests/test_scratch_notes.py`
- **Files to Modify:** 0
- **Verification to Add:** 1 test module, about 60 test cases: about 45 rule cases that
  call the functions, and about 15 command cases that run the script as a process
- **Estimated Complexity:** L
- **Requirements covered:** FR-001, FR-002, FR-003, FR-004, FR-006, FR-008, FR-009,
  FR-010, FR-011, FR-013, FR-017

## Codebase Conventions

- **File naming:** `scratch_notes.py` at the repository root, the exact name the
  requirements fix. The test module is `tests/test_scratch_notes.py`, a name pytest
  discovers. Create no `tests/__init__.py`, no `conftest.py` and no pytest
  configuration: the last two would make the kit's setup check read STALE.
- **Import order:** standard library only, in one block, as ruff's defaults sort it.
  The script imports `os`, `re`, `stat` and `sys`, after
  `from __future__ import annotations`. Nothing else, and not `json` yet: MAX-100 adds it.
- **Naming:** functions and variables in lowercase with underscores; classes in
  CapWords; module constants in capitals; compiled patterns and other non-public names
  with one leading underscore; every exception class ends in `Error`.
- **Error handling:** invalid input raises one of the error classes in C3. Nothing
  returns a sentinel or a partial result. A message names the failing input.
- **Documentation:** a module docstring saying what the file does and how to run it,
  and a docstring on every public function and class saying what it takes, returns and
  raises.
- **Type checking:** every function annotated; `uv run mypy scratch_notes.py tests/`
  is clean.
- **Lint and format:** `uv run ruff check scratch_notes.py tests/` and
  `uv run ruff format --check scratch_notes.py tests/` are clean, with default rules.
- **Verification framework:** pytest, pinned by `uv.lock`, with no configuration. A
  plain `uv run pytest` from the repository root collects the test module.

## Technical Context

**Key gotchas:**

- **The file must parse under Python 3.9.** FR-013 needs the version guard to run on
  `/usr/bin/python3`, so the whole file, not only the guard, must be free of syntax
  newer than 3.9: no `match`, no `except*`, no parenthesised context managers. Postponed
  annotations make modern annotation forms safe, because they are never evaluated.
- **No `argparse`, `dataclasses` or `typing`.** Together they add about 7 ms of start-up
  (measured in `design/1a-discovery.md`), and `argparse` would add a help screen on
  stdout and option abbreviations the contract doesn't want. The value shapes are small
  plain classes.
- **Tests reach the script by its file location.** A test under `tests/` cannot
  `import scratch_notes`: the repository root is not on the import path, and the
  project is not installed. Load the file once with `importlib`, under the module name
  `scratch_notes`, so coverage can measure it. Never change `sys.path`. This departs
  from the project rubric's line that tests reach the code "as an installed
  distribution": the requirements exclude packaging, and requirements outrank the
  rubric under config's `nfr_precedence` (ADR-001). Verification should treat it as
  this named exception.
- **Later units extend these two files.** Write the tests so MAX-99 and MAX-100 can add
  behaviour without editing them:
  - Assert exact plain output only on files that hold no heading lines, or assert the
    first line only. MAX-99 adds heading lines after `open: N`.
  - Compare a summary's `open_count`, not the whole summary object. MAX-99 adds a
    field.
  - Use `--verbose`, not `--json`, as the unknown option. MAX-100 makes `--json` valid.
  - Assert that a usage message starts with `scratch_notes: usage:` and holds the
    reason, not its full text. MAX-100 adds `[--json]` to it.
- **Split lines at line feeds only.** Python's `splitlines` also breaks at form feeds
  and Unicode line separators, which would invent lines the file doesn't have.
- **Spaces and tabs only.** The line rules and the trimming of trailing whitespace must
  not use a "any whitespace" class or a bare `strip`: a non-breaking space is not
  indentation.
- **Stdout and stderr are written as bytes.** `main` encodes to UTF-8 itself, so the
  output does not depend on the terminal's locale.

**Reusable utilities:** none exist; the repository has no source modules.

**Integration points:**
- MAX-99 extends `scan_notes`, `render_plain` and the summary shape.
- MAX-100 extends `parse_arguments`, `run` and the request shape, and adds
  `render_json`.
- MAX-102, the integration unit, runs the finished script end to end.

## Contract

Implement, exactly as `design/1b-contracts.md` defines them:

- **C1, plain mode only:** `python3 scratch_notes.py <file>` prints `open: N` and a
  line feed on stdout and exits 0. Every failure prints one line,
  `scratch_notes: <message>`, on stderr, leaves stdout empty and exits non-zero.
- **C2:** `check_python_version`, `parse_arguments`, `read_notes`, `scan_notes`,
  `render_plain`, `run` and `main`, with the signatures, order of work and purity that
  C2 states. In this unit `parse_arguments` accepts one file and no option,
  `scan_notes` counts open items and tracks fences, and `render_plain` returns the
  `open: N` line.
- **The data shapes:** a request holding `path`; a summary holding `open_count`; a
  result holding `exit_code`, `stdout` and `stderr`.
- **The line rules:** the fence opener, the open item and the fence closer, with every
  row of the edge-case table that concerns open items and fences. The heading rule is
  MAX-99's.
- **C3:** the whole error family. Exit code 2 for `UsageError`, 1 for every other.

**Messages, after `scratch_notes: `.** `<path>` is the path in escaped ASCII inside
quotes, as Python's `ascii` renders text.

| Error | Message |
|---|---|
| `UsageError` | `usage: scratch_notes.py <file> (<reason>)`, where the reason is `expected one file, got <count>` or `unknown option <option>` |
| `UnsupportedPythonError` | `needs Python 3.11 or newer, running <major>.<minor>.<micro>` |
| `NotesFileMissingError` | `no such file: <path>` |
| `NotARegularFileError` | `not a regular file: <path>` |
| `NotesFileTooLargeError` | `larger than 1048576 bytes: <path>` |
| `NotesFileUnreadableError` | `cannot read <path>: <the operating system's reason>` |
| `NotesFileEncodingError` | `not valid UTF-8: <path>` |
| `UnclosedFenceError` | `code fence opened on line <number> is never closed` |

## Task Breakdown

### Task 1: Write the test module first

**Dependencies:** None

**Files to Create:**
| File | Purpose |
|------|---------|
| `tests/test_scratch_notes.py` | Rule tests and command tests for this unit |

**Pattern Reference:** follow
`.ai-delivery/features/pull-request-checklist/checks/test_contributing.py` for the
module docstring, the annotated and documented test functions, the arrange, act, assert
layout, and adverse cases on inline samples. Two deviations: this module lives in
`tests/`, inside pytest's default run, and it loads the code under test by file
location because that code is a script, not a module beside it.

**Implementation Algorithm:**
1. Resolve the repository root from the module's own path, and from it the script's
   path. Read no environment variable.
2. Load the script once by file location, under the name `scratch_notes`, without
   touching `sys.path`.
3. Add one small helper that runs the script as a process with a given interpreter,
   extra interpreter flags and arguments, with a timeout of a few seconds, and returns
   the exit code, stdout and stderr.
4. Build each test's input inline or in pytest's temporary directory.

**Rule cases: the open-item rule** (FR-002; each form is its own case):
- `- [ ] task`, `* [ ] task` and `+ [ ] task` each count as one.
- Indented with spaces, with a tab, and with both: counts.
- Two spaces, and a tab, between the marker and `[ ]`: counts.
- A bare `- [ ]` with nothing after it: counts.
- `- [ ]buy milk`, with no space after the bracket: counts.
- `- [x]`, `- [X]` and `- [-]`: do not count.
- `- []`, `- [  ]` and `-[ ]`: do not count.
- `1. [ ]`: does not count.
- `> - [ ]`: does not count.
- A marker followed by a non-breaking space, then `[ ]`: does not count.
- A file mixing several of these gives the sum of the open ones.
- An empty file gives 0, and so does a file of only blank lines.

**Rule cases: fences** (FR-003, FR-004):
- An open item inside a backtick fence does not count; one before and one after do.
- The same with a tilde fence.
- A fence with a language name after the backticks is a fence.
- A fence indented under a list item is a fence, and its closer may be indented.
- A backtick line inside a tilde fence does not close it, and a tilde line inside a
  backtick fence does not close it.
- A closer shorter than its opener does not close the fence; a longer one does.
- A closer followed by trailing spaces closes; a closer followed by text does not.
- A one-line snippet that opens and closes with three backticks is text: an open item
  on the next line counts.
- `~~~` followed by text opens a fence.
- A file ending inside a fence raises `UnclosedFenceError` whose message names the
  line where the fence opened; check a fence opened on line 1 and one opened later.

**Rule cases: line endings and the byte-order mark** (FR-006):
- A CRLF copy of a sample gives the same count as the LF original.
- A file starting with a UTF-8 byte-order mark and an open item on line 1 counts it.
- A form feed or a Unicode line separator inside a line does not split it: text, then
  that character, then `- [ ]` on the same line does not count.

**Rule cases: `read_notes`** (FR-006, FR-009, FR-010, FR-017):
- A regular file returns its text.
- A symbolic link to a regular file is read.
- A missing path, and a path under a missing directory, raise `NotesFileMissingError`.
- A directory raises `NotARegularFileError`.
- A file with all permissions removed raises `NotesFileUnreadableError`; skip with a
  stated reason when running as the superuser.
- Bytes that are not valid UTF-8 raise `NotesFileEncodingError`.
- A file of exactly 1,048,576 bytes is read.
- A file of 1,048,577 bytes raises `NotesFileTooLargeError`, and its message names
  1048576.
- When the size lookup reports a size within the limit but the file yields more than
  the limit, `NotesFileTooLargeError` is still raised. Replace the size lookup for
  this one case; assert the error, not that the replacement was called.
- Every message holding a path shows it in escaped ASCII and is one line, checked
  with a path that holds a space and a non-ASCII character.

**Rule cases: arguments, version guard and `run`** (FR-001, FR-009, FR-013):
- One path gives a request holding that path, exactly as given.
- No argument, and two paths, raise `UsageError` naming the count.
- `--verbose`, `-`, `--` and `--help` each raise `UsageError` naming the option.
- `./-name` is accepted as a path.
- `check_python_version` raises `UnsupportedPythonError` for 3.9.6 and 3.10.99, with
  the running version in the message, and returns for 3.11.0 and 3.14.5.
- `run` on a good file returns exit code 0, `open: N` and a line feed as stdout, and
  empty stderr.
- `run` for each failure returns the exit code C3 names, empty stdout, and one stderr
  line that starts with `scratch_notes: ` and ends with a line feed. Cover: usage,
  missing file, directory, oversized file, invalid UTF-8 and unclosed fence.

**Command cases** (the script run as a process, with the interpreter running the tests):
- A good file: exit 0, stdout `open: N` and a line feed, stderr empty.
- The same run with the interpreter flags `-I -S`: the same result (FR-011).
- A named pipe as the path, with the timeout: non-zero exit before the timeout, stdout
  empty (FR-010). Skip with a stated reason where named pipes can't be created.
- `/dev/null` as the path: non-zero exit, stdout empty. Skip with a stated reason
  where it doesn't exist.
- No argument: exit 2, stdout empty, one stderr line.
- A missing file: exit 1, stdout empty, one stderr line.
- An unclosed fence: exit 1, stdout empty, one stderr line naming the line.
- Read only: record the file's bytes and its modification time in nanoseconds, run
  once on a good file and once on a file with an unclosed fence, and find both
  unchanged (FR-001).
- Old Python: when `/usr/bin/python3` exists and reports a version below 3.11, running
  the script with it exits non-zero, prints nothing on stdout, and names 3.11 on
  stderr in one line that is not a traceback. Skip with a stated reason otherwise
  (FR-013).

**Expected state after Task 1:** every test fails or errors, because `scratch_notes.py`
does not exist.

**Critical Notes:**
- Every test asserts an outcome: a count, an error class and message, an exit code, an
  exact output. None asserts only that something was called.
- Tests share no state. Each builds its own files.

---

### Task 2: The error family, the value shapes, the version guard and the arguments

**Dependencies:** Task 1
**Files:** `scratch_notes.py` (create)
**Pattern:** `test_contributing.py`, for the module docstring, constants, annotations
and docstrings
**Implementation:** Write the module docstring and the size-limit and minimum-version
constants. Define `ScratchNotesError` carrying a message and an exit code, and one
subclass per row of the message table above. Define the request, summary and result
shapes as small plain classes. `check_python_version` compares the version it is given
with 3.11. `parse_arguments` sorts the arguments into options, which start with `-`,
and paths; any option is unknown in this unit, and anything other than exactly one path
is a usage error. Report an unknown option before a wrong path count.
**Verification:** the arguments and version-guard rule cases pass.

---

### Task 3: `read_notes`

**Dependencies:** Task 2
**Files:** `scratch_notes.py` (modify)
**Modification note:** `scratch_notes.py` — add `read_notes` after `parse_arguments`.

**Contract:** `read_notes` in C2, and "How `read_notes` keeps its promises" in C3.

**Implementation Algorithm:**
1. Look the path up once, following symbolic links. A path that doesn't exist, or
   whose parent is not a directory, is `NotesFileMissingError`. Any other refusal by
   the operating system is `NotesFileUnreadableError`, carrying its reason.
2. From that one lookup: anything that is not a regular file is
   `NotARegularFileError`; a recorded size over the limit is `NotesFileTooLargeError`.
   Both are decided before anything is opened.
3. Open the file for reading as bytes and read at most the limit plus one byte. Close
   it before going on, on success and on failure. A refusal by the operating system
   here is `NotesFileUnreadableError`.
4. More bytes than the limit is `NotesFileTooLargeError`.
5. Decode strictly as UTF-8; a failure is `NotesFileEncodingError`. Remove one
   byte-order mark at the very start, and nowhere else.

**Cases:** the `read_notes` rule cases in Task 1.

**Critical Notes:**
- Never open before the file-type check: opening a named pipe for reading blocks.
- The message never carries any of the file's bytes.

---

### Task 4: `scan_notes`: fences and open items

**Dependencies:** Task 2
**Files:** `scratch_notes.py` (modify)
**Modification note:** `scratch_notes.py` — add the line patterns as module constants
beside the other constants, and `scan_notes` after `read_notes`.

**Contract:** "The line rules behind `scan_notes`" in `design/1b-contracts.md`, without
the heading rule.

**Implementation Algorithm:**
1. Split the text at line feeds and remove one trailing carriage return from each
   line. Number lines from 1.
2. Outside a fence, test the fence-opener rule first, then the open-item rule.
3. Inside a fence, test only the closer rule: the fence's own character, at least as
   many times as the opener, then optional trailing whitespace.
4. At the end, a fence still open raises `UnclosedFenceError` with the opener's line
   number.

**Cases:** the open-item, fence, line-ending and byte-order-mark rule cases in Task 1.

**Critical Notes:**
- Apply each pattern to the whole line, with no nested repetition, so no line of up to
  1 MiB can make matching slow.
- The function is pure: no file, no clock, no environment.

---

### Task 5: `render_plain`, `run`, `main` and the script entry

**Dependencies:** Tasks 3 and 4
**Files:** `scratch_notes.py` (modify)
**Modification note:** `scratch_notes.py` — add the three functions after `scan_notes`,
and the script entry as the last lines of the file.
**Implementation:** `render_plain` returns `open: N` and a line feed. `run` calls the
version guard with the running interpreter's version, then the arguments, the read, the
scan and the renderer, in that order; it catches `ScratchNotesError` and nothing wider,
and returns a result either way. `main` passes the process's arguments to `run`, writes
the result's stdout and stderr as UTF-8 bytes to the process's two streams, and returns
the exit code. Run as a script, the file exits with `main`'s return value; loaded by
location, it runs nothing.
**Verification:** the `run` rule cases and every command case pass.

---

### Task 6: Quality pass

**Dependencies:** Task 5
**Files:** no new files.
**Implementation:** run, from the repository root:
- `uv run pytest`
- `uv run pytest --cov=scratch_notes --cov-branch --cov-report=term-missing`
- `uv run ruff check scratch_notes.py tests/`
- `uv run ruff format --check scratch_notes.py tests/`
- `uv run mypy scratch_notes.py tests/`
- `uv run bandit -ll scratch_notes.py`

Fix whatever fails, then run the suite once more.

**Verification:**
- Every command exits 0, and coverage of `scratch_notes.py` is at least 80% of lines
  and 70% of branches.
- `git status --short` shows only `scratch_notes.py` and `tests/` as new, with no
  `__pycache__` or cache directory left unignored.

## Task Dependency Graph

```
Task 1: test module, written first; every test fails, the script is missing
    │
    └─→ Task 2: error family, value shapes, version guard, arguments
            │
            ├─→ Task 3: read_notes
            │       │
            ├─→ Task 4: scan_notes (fences and open items)
            │       │
            └───────┤
                    │
                    └─→ Task 5: render_plain, run, main, script entry
                            │
                            └─→ Task 6: suite, coverage, ruff, mypy, bandit
```

## Pattern References

- **Verification and style pattern:**
  `.ai-delivery/features/pull-request-checklist/checks/test_contributing.py` — its
  module docstring, constants, compiled patterns as underscored module constants,
  annotated and documented functions, and tests laid out as arrange, act, assert with
  adverse cases on inline samples.

## Implementation Notes

- **Performance:** one read, one pass, four imports. Do not add an import to save a few
  lines of code; start-up time is the budget (`design/1c-operations.md`).
- **Security:** the path goes only to the operating system's file calls. The script
  starts no process and evaluates no text. Error messages carry the path, never file
  content.
- **Deployment:** none in this unit. Commit nothing; the user handles commits at
  handoff.
- **Rubric notes:**
  - The contract other units build on is the set of function signatures and shapes in
    C2, fixed before any code. Abstract classes for a one-file script would add code
    with no second implementation to serve.
  - `read_notes` is tested on real files in pytest's temporary directory, because the
    behaviour under test is the filesystem's. Every other function is tested with
    inline text alone.
  - Coverage reports the script-entry line as missed; only the command tests reach it.

## Final Verification

**Functionality:**
- [ ] Every acceptance criterion in MAX-98 and its Prototype notes is met, and FR-001,
  FR-002, FR-003, FR-004, FR-006, FR-008, FR-009, FR-010, FR-011, FR-013 and FR-017
  are each covered by at least one test.
- [ ] Every failure exits non-zero with empty stdout and one line on stderr.

**Code quality:**
- [ ] The script imports only `os`, `re`, `stat` and `sys`, and parses under
  Python 3.9.
- [ ] Clean under ruff check, ruff format, mypy and bandit; fully annotated and
  documented; no debug leftovers and no commented-out code.

**Testing:**
- [ ] The test module was written first and failed before the script existed.
- [ ] `uv run pytest` passes, and coverage of the script is at least 80% of lines and
  70% of branches.
- [ ] No test changes `sys.path`, and no `conftest.py` or pytest configuration exists.

**Build:**
- [ ] Only `scratch_notes.py` and `tests/test_scratch_notes.py` are created, and
  nothing else in the working tree changes.
