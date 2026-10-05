# Design contracts: Scratch notes

This document fixes what `scratch_notes.py` promises: what the command prints and how it
exits, what each of its functions takes and returns, every way it can fail, and how each
promise is tested. It matters because three units are built one after another in the
same two files, and the developer's shell prompt relies on stdout, stderr and the exit
code without ever seeing the code.

**Date:** 2026-10-01
**Feature directory:** `.ai-delivery/features/scratch-notes/`
**Builds on:** `design/1a-discovery.md`
**Status:** contracts and testing strategy, version 1

> **Terms used here.** MAX-82, MAX-83 and MAX-84 are the Linear issues for the three
> units: the open count, the headings, and the `--json` output. FR-001 to FR-017 are the
> requirement labels in `requirements.md`. The *prompt* is the developer's own shell
> prompt script, outside this repository. C1 to C4 are the contracts defined below.
> ADR-001 and ADR-002 are the two architecture decision records in `1a-discovery.md`.
> A *line* is the text between two line feeds, with one trailing carriage return
> removed. *Indentation* and *trailing whitespace* mean spaces and tabs only.

## Contracts

### Patterns shared by every contract

- **Authentication and authorization:** none. The script is a local command run by the
  developer on the developer's own files. The operating system's file permissions are
  the only access control, and a file the user can't read is a failure (C3).
- **One result per run.** A run produces either a result on stdout with exit code 0, or
  one line on stderr with a non-zero exit code and empty stdout. Never both, never
  neither.
- **Versioning.** The JSON carries no version field (brief § 6). The prompt is the only
  reader and has the same owner. A change to a key, to the plain-text layout or to an
  exit code is a revision of the requirements, not a quiet edit.
- **Pagination, caching, rate limits:** not applicable. One file, one process, no state
  kept between runs.

### C1: The command

**Purpose.** Report one notes file's open count and headings.

**Invocation.**

| Form | Accepted from | Meaning |
|---|---|---|
| `python3 scratch_notes.py <file>` | MAX-82 | Plain text |
| `python3 scratch_notes.py <file> --json` | MAX-84 | One line of JSON |
| `python3 scratch_notes.py --json <file>` | MAX-84 | The same; the option may come first |

**Argument rules.**
- Exactly one argument must be a file path. Zero or two or more is a usage error.
- An argument that starts with `-` is an option. The only option is `--json`, from
  MAX-84 on, and it may be given once. Any other option is a usage error, including
  `-`, `--`, `--help` and a second `--json`. Until MAX-84 lands, `--json` is itself an
  unknown option.
- A file whose name starts with `-` is passed as `./-name`.
- The path is used exactly as given. The script never searches for a file.

**Output on success (exit code 0, stderr empty).**

| Mode | Stdout | From |
|---|---|---|
| Plain | First line `open: N`. Then one line per heading, in file order. | Count line: MAX-82. Heading lines: MAX-83. |
| JSON | Exactly one line: `{"open": N, "headings": [...]}` | MAX-84 |

- `N` is a whole number in decimal with no padding.
- Each heading is the line exactly as written, `#` marks included, without its line
  ending or trailing whitespace.
- A file with no headings prints only `open: N` in plain mode.
- An empty file gives `open: 0` in plain mode and `{"open": 0, "headings": []}` in
  JSON mode.
- The JSON object has exactly two keys, `open` first, then `headings`. `open` is a JSON
  number and `headings` is a JSON array of strings. The separators are a comma and a
  space between items and a colon and a space after each key. Characters outside ASCII
  are written as `\u` escapes, so the line is pure ASCII and decodes back to the
  headings as written.
- Stdout always ends with one line feed and is written as UTF-8 bytes, whatever the
  terminal's locale.

**Output on failure (exit code non-zero, stdout empty).** One line on stderr:
`scratch_notes: <message>`. The full list is C3.

**Side effects.** None. The file is opened for reading only. Its bytes and modification
time are the same after every run, successful or not.

**Time.** Each call finishes within 50 ms on a notes-like file at the size limit, timed
end to end with the prompt's interpreter (FR-012).
**[REVISED in MAX-84, 2026-10-02]:** this said "a file at the size limit". The time
follows the number of lines, so a 1 MiB file of very short lines can take up to about
165 ms.

### C2: The functions

These signatures are the seams between the three units. A later unit may extend a
function's behaviour as the table says. It may not change a signature, an error or a
return shape that an earlier unit delivered.

| Function | Purpose | Takes | Returns | Raises | Delivered by |
|---|---|---|---|---|---|
| `check_python_version` | Refuse to run on an old Python | A version as three whole numbers: major, minor, micro | Nothing | `UnsupportedPythonError` when the version is below 3.11 | MAX-82 |
| `parse_arguments` | Turn the arguments into a request | The arguments after the script name, as a list of text | A CommandRequest | `UsageError` | MAX-82; MAX-84 adds `--json` |
| `read_notes` | Read one regular file as text | A path, as text | The file's text, without a leading byte-order mark | `NotesFileMissingError`, `NotARegularFileError`, `NotesFileTooLargeError`, `NotesFileUnreadableError`, `NotesFileEncodingError` | MAX-82 |
| `scan_notes` | Apply the line rules | The file's text | A NotesSummary | `UnclosedFenceError` | MAX-82 for the count and fences; MAX-83 adds headings |
| `render_plain` | Lay out plain text | A NotesSummary | Text ending in a line feed | Nothing | MAX-82 for the count line; MAX-83 adds heading lines |
| `render_json` | Lay out the JSON line | A NotesSummary | Text ending in a line feed | Nothing | MAX-84 |
| `run` | Do one whole run without touching stdout or stderr | The arguments after the script name | A CommandResult | Nothing from the error family: each one becomes a CommandResult | MAX-82; MAX-84 adds the choice of renderer |
| `main` | Write a CommandResult out and report the exit code | Nothing; it reads the process's own arguments | The exit code | Nothing from the error family | MAX-82 |

**Behaviour that the table doesn't show.**

- **`run` works in a fixed order:** version guard, arguments, read, scan, render. The
  version guard comes first, so an old Python is reported even when the arguments are
  also wrong.
- **`run` builds the whole result before returning it.** Nothing reaches stdout until
  the scan has finished, so a failure can never follow partial output.
- **`scan_notes` is pure.** It reads no file, no clock and no environment, and the same
  text always gives the same summary.
- **`read_notes` is the only function that touches the filesystem**, and it closes what
  it opens before returning, on success and on failure.
- **The whole file parses under Python 3.9.** It uses postponed annotations and no
  syntax newer than 3.9, so the version guard can run on `/usr/bin/python3`.
- **Imports are limited** to `json`, `os`, `re`, `stat` and `sys`. `argparse`,
  `dataclasses` and `typing` are left out for start-up time (measured in
  `1a-discovery.md`).
- **Running the file as a script** calls `main` and exits with its return value.
  Loading the file by its location, as the tests do, runs nothing.

### Data shapes

```
CommandRequest
├── path: text; the one file to read, exactly as given
└── as_json: true or false; added by MAX-84

NotesSummary
├── open_count: whole number, zero or more
└── headings: ordered list of text; added by MAX-83

CommandResult
├── exit_code: 0 on success; above zero on failure
├── stdout: text; empty on failure
└── stderr: text; empty on success, otherwise one line ending in a line feed
```

### The line rules behind `scan_notes`

The text is split into lines at line feeds only. One trailing carriage return is removed
from each line, so CRLF and LF files scan alike. A carriage return on its own, a form
feed and the Unicode line separators do not end a line. Lines are numbered from 1.

Each rule is applied to the whole line, from its first character.

**Outside a fence, the first rule that fits decides the line:**

1. **Fence opener** (FR-003). After any indentation, the line starts with a run of
   three or more backticks and holds no backtick after that run, or it starts with a
   run of three or more tildes. The scan enters a fence and remembers the character,
   the length of the run and the line number.
2. **Open item** (FR-002). After any indentation: one of `-`, `*` or `+`, then one or
   more spaces or tabs, then exactly `[ ]`. Anything, or nothing, may follow. The open
   count goes up by one.
3. **Heading** (FR-005, from MAX-83). With no indentation: one to six `#`, then a
   space, a tab or the end of the line. The line, without trailing whitespace, joins
   the headings.
4. **Anything else** is ignored.

**Inside a fence, only one rule applies:**

- **Fence closer.** After any indentation, the line holds only the fence's own
  character, at least as many times as the opener, then optional trailing whitespace.
  The scan leaves the fence. Every other line inside a fence is ignored, including
  lines that look like open items, headings or openers of the other kind.

**At the end of the text,** a fence still open is an `UnclosedFenceError` carrying the
line number where it opened (FR-004).

**Decided edge cases, each one a test case:**

| Line | Outcome | Why |
|---|---|---|
| `- [ ]` with nothing after it | Open | Anything or nothing may follow (FR-002, revised) |
| `- [ ]buy milk` | Open | The same |
| `- [x]`, `- [X]`, `- [-]` | Not open | Not exactly `[ ]` |
| `- []`, `- [  ]`, `-[ ]` | Not open | Not a checkbox under the rule |
| `1. [ ]` | Not open | Numbered items don't count |
| `> - [ ]` | Not open | Doesn't start with a list marker after indentation |
| `-` followed by a non-breaking space, then `[ ]` | Not open | A non-breaking space is not a space or a tab |
| `#tag`, `#######`, a heading underlined with `===` or `---` | Not a heading | FR-005 |
| ` # indented` | Not a heading | Headings take no indentation |
| `#` alone, or `##` followed only by spaces | A heading, reported as `#` or `##` | The end of the line may follow the marks |
| A one-line snippet that opens and closes with three backticks | Text, not a fence | FR-003, revised |
| `~~~` followed by text | Opens a fence | Tilde fences are unchanged |
| A backtick line inside a tilde fence | Ignored | Only the fence's own character closes it |
| A closer shorter than its opener | Ignored; the fence stays open | The closer must be at least as long |
| An indented fence under a list item | A fence | Any indentation is allowed |
| A heading on line 1 after a byte-order mark | A heading | The mark is removed before the scan (FR-006) |

### C3: Failures

Every failure is one class in a family whose base is `ScratchNotesError`. Each carries
its message and its exit code, and `run` turns it into a CommandResult. Paths appear in
messages in escaped ASCII inside quotes, so a message is always one line, whatever the
path contains.

| Error | When | Exit code | Message after `scratch_notes: ` | Raised by |
|---|---|---|---|---|
| `UsageError` | Zero files, two or more files, or an unknown or repeated option | 2 | `usage: scratch_notes.py <file> [--json]`, then the reason in brackets; before MAX-84 the usage text has no `[--json]` | `parse_arguments` |
| `UnsupportedPythonError` | The running Python is older than 3.11 | 1 | `needs Python 3.11 or newer, running <version>` | `check_python_version` |
| `NotesFileMissingError` | The path doesn't exist, or a directory in it doesn't | 1 | `no such file: <path>` | `read_notes` |
| `NotARegularFileError` | The path is a directory, a named pipe, a device or a socket; checked before anything is opened | 1 | `not a regular file: <path>` | `read_notes` |
| `NotesFileTooLargeError` | The file is over 1,048,576 bytes when checked, or yields more than that when read | 1 | `larger than 1048576 bytes: <path>` | `read_notes` |
| `NotesFileUnreadableError` | The operating system refuses to check or read the file, for example on permissions | 1 | `cannot read <path>`, then the operating system's reason | `read_notes` |
| `NotesFileEncodingError` | The bytes are not valid UTF-8 | 1 | `not valid UTF-8: <path>` | `read_notes` |
| `UnclosedFenceError` | The text ends inside a fence | 1 | `code fence opened on line <number> is never closed` | `scan_notes` |

**What is not in the family.** An exception the design did not foresee is not caught.
Python prints its traceback on stderr and exits with code 1, and stdout is still empty
because nothing is written before the result is complete. The prompt shows `?` either
way.

**How `read_notes` keeps its promises.**
- A symbolic link is followed, so a link to a regular file is read and a link to a
  directory is refused.
- The size is checked twice: from the file's recorded size before opening, and by
  reading at most the limit plus one byte. A file that grows between the two is still
  refused, and the script never holds more than the limit plus one byte.
- A file of exactly 1,048,576 bytes is read.
- A byte-order mark is removed only at the very start of the file.

### C4: The tests

One file, `tests/test_scratch_notes.py`, with no `conftest.py` and no pytest
configuration (ADR-002). It holds two groups (ADR-001).

- **Rule tests** load `scratch_notes.py` by its file location and call the functions in
  C2. They need no process. Tests of `read_notes` use real files in pytest's temporary
  directory, because the behaviour under test is the filesystem's.
- **Command tests** run the script as a process and check stdout, stderr and the exit
  code, each with a timeout so a hang fails the test, not the run.

Every test asserts an outcome: a count, a list of headings, an exact output text, an
error class, an exit code. None asserts only that something was called.

## Integration points

- **Events published or consumed:** none.
- **External service calls:** none. The script makes no network call and starts no
  process.

### What the script depends on

| Dependency | Criticality | When it fails | Handling |
|---|---|---|---|
| A Python 3.11 or newer on the path the prompt calls | Critical | The script can't run, or runs on an old Python | An old Python is refused with a message (FR-013). A missing interpreter is the prompt's failure, and it shows `?`. |
| The notes file | Critical | Missing, unreadable, too large, not text | A named failure in C3 |
| The standard library modules `json`, `os`, `re`, `stat`, `sys` | Critical | Not possible on a working Python | The `python3 -I -S` test proves nothing else is needed (FR-011) |

### What depends on the script

| Consumer | Uses | What it relies on | Effect of a breaking change |
|---|---|---|---|
| The prompt | `--json` on every draw | Exit code 0 with one JSON line holding `open`; non-zero otherwise; an answer within 50 ms | The count disappears or shows `?` in every project |
| The developer | Plain mode, by hand | `open: N` first, then the headings | A misread count |

## Testing strategy

### Unit testing: the rule tests

**Coverage targets.** Those in `.ai-delivery/gates.md`: 80% of lines and 70% of
branches, measured with `uv run pytest --cov=scratch_notes --cov-branch
--cov-report=term-missing`. The feature adds no stricter target. The one line that
calls `main` when the file is run as a script is reached only by the command tests and
is reported as missed.

**Written first, by unit.**

| Unit | Cases written before the code |
|---|---|
| MAX-82 | Every row of the edge-case table that concerns open items and fences; fences in backticks and tildes, nested under a list item, a backtick line inside a tilde fence, an unclosed fence with its line number; CRLF against LF; a byte-order mark; an empty file; each `read_notes` failure; exactly 1 MiB accepted and one byte more refused; a file that reports a small size but yields more than the limit; each usage error; the version guard with 3.9.6, 3.10.99 and 3.11.0; the `open: N` line; `run` returning the right exit code, stdout and stderr for each failure |
| MAX-83 | Every row of the edge-case table that concerns headings; headings inside both kinds of fence; trailing whitespace removed; a heading after a byte-order mark; file order kept; heading lines after `open: N`; no headings |
| MAX-84 | `--json` before and after the file; a repeated `--json`; the exact JSON text for a small file; the two keys and their types after parsing; an empty file; a heading with non-ASCII text decoding back as written; every failure with `--json` still giving empty stdout and a non-zero exit |

**Isolation.** Each test builds its own input, inline or in pytest's temporary
directory. No test reads the clock, the network, the environment or another test's
files. The standard library is not mocked, with one exception: the size test replaces
the file-size lookup to show the bounded read refuses a file that grew.

### Integration testing: the command tests

There is no database and no service. Integration here means the script run as a process.

| Scenario | How | Expected outcome | Unit |
|---|---|---|---|
| Plain run | `<test interpreter> scratch_notes.py <file>` | Exit 0, `open: N`, stderr empty | MAX-82 |
| Standard library only | `<test interpreter> -I -S scratch_notes.py <file>` | Exit 0 and the same output (FR-011) | MAX-82 |
| Named pipe | The path is a named pipe; timeout of a few seconds | Exit non-zero before the timeout, stdout empty (FR-010) | MAX-82 |
| Directory and device | The path is a directory, then `/dev/null` | Exit non-zero, stdout empty | MAX-82 |
| Missing file, unreadable file, invalid UTF-8, unclosed fence, usage error, oversized file | One run each | Exit non-zero, one line on stderr, stdout empty (FR-009) | MAX-82 |
| Read only | Record bytes and modification time, run on success and on failure, compare | Unchanged (FR-001) | MAX-82 |
| Old Python | Run with `/usr/bin/python3` when it exists and is older than 3.11; skipped with a stated reason otherwise | Exit non-zero, a message naming 3.11, stdout empty (FR-013) | MAX-82 |
| Plain run with headings | As the plain run | `open: N`, then the headings | MAX-83 |
| JSON run | `… <file> --json` | Exit 0 and one JSON line | MAX-84 |
| Timing | 20 runs of `/opt/homebrew/bin/python3 scratch_notes.py <sample> --json` on a sample at the size limit; skipped with a stated reason when that interpreter is absent | The slowest run is under 50 ms; all 20 timings are shown in the test's output (FR-012) | MAX-84 |

**Test data.** A sample builder in the test file makes a notes file of a requested size
from repeating blocks of headings, open items, done items, nested items and fenced code
holding look-alike lines. It returns the text together with the count and headings that
are correct by construction, so the same sample serves the correctness test at 1 MiB
and the timing test.

### Contract testing

- **C1** is checked by the command tests: exact stdout for small files in both modes,
  the JSON parsed and its keys and types checked, and stderr and the exit code for
  every failure in C3.
- **C2** is checked by the rule tests, one function at a time.
- **Across units,** MAX-83 and MAX-84 must leave every earlier test passing unchanged.
  The whole suite runs after each unit, which is what catches a later unit breaking an
  earlier contract.

### Load and performance testing

No load tool is needed for a single short process. The timing scenario above is the
performance test. ~~It runs at the worst case the script accepts.~~
**[REVISED in MAX-84, 2026-10-02]:** it runs on a notes-like sample at the largest size
the script accepts, which is not the slowest possible content.

### End-to-end testing

Three journeys, proven at integration on one sample file:

1. **The prompt's journey.** The JSON run exits 0, and the prompt can read `open` from
   one line.
2. **The developer's journey.** The plain run on the same file shows the same count as
   the JSON run, and the same headings in the same order.
3. **The failure journey.** Each failure in C3, in both modes, leaves stdout empty,
   puts one line on stderr and exits non-zero.

## Design quality gate

The three checks the software profile adds, applied to the seams above.

| Check | Result | Basis |
|---|---|---|
| Interface first | Pass, with a note | The seams are function signatures and three data shapes, fixed in C2 before any code. No consumer depends on a concrete class. Abstract classes for a one-file script would add code with no second implementation to serve. |
| Testable | Pass | `parse_arguments`, `scan_notes`, both renderers and the version guard are pure and need nothing but their arguments. Only `read_notes` touches the filesystem, and it is one small function. |
| Replaceable | Pass | The scan can be rewritten behind `scan_notes`, and a renderer added beside the two that exist, without touching a consumer. The prompt depends on C1 alone. |

## Revision history

| Date | Change | Reason | Rework ID |
|------|--------|--------|-----------|
| 2026-10-02 | The 50 ms limit is promised for a notes-like file at the size limit, not for every file the script accepts. | Timing the real script at 1 MiB took at most 33 ms on a notes-like mix, 47 ms with an open item on every line and 165 ms on empty lines only: the time follows the number of lines. Max Adamsky kept the 1 MiB limit and restated the promise. | MAX-84 |

## Next steps

`1c-operations.md` covers security, performance against the 50 ms limit, how the script
reaches the prompt, rollback and risks.

This document surfaced nothing requiring a decision or an action beyond the open items
already listed in `1a-discovery.md`.
