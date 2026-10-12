# Design discovery: Scratch notes 3.0.2 live proof

This design covers scratch-notes: one standard-library Python script, `scratch_notes.py`
at the repository root, that reads one Markdown notes file and prints how many checklist
items are still open, plus the file's headings, as plain text or as JSON. It matters
because the developer's shell prompt will show that count on every project switch, and
the grep used today miscounts it, so the number can't be trusted.

**Profile:** software (of config: software)
**Date:** 2026-10-01
**Feature directory:** `.ai-delivery/features/scratch-notes/`
**Linear project:** P-MAX-15 Scratch notes 3.0.2 live proof —
https://linear.app/max-test-workspace/project/scratch-notes-302-live-proof-bd6ecd9d3df9
**Work issues:** MAX-98 (the open count), MAX-99 (the headings) and MAX-100 (the `--json`
output). MAX-101 (the `CONTRIBUTING.md` update) was dropped on 2026-10-01.
**Requirements:** `requirements.md` in the feature directory, approved 2026-09-30 and
revised 2026-10-01
**Discovery brief:** `brief.md` in the feature directory

> **Terms used here.** MAX-98 to MAX-101 are the Linear issues that track the units of
> work. FR-001 to FR-017 are the requirement labels in `requirements.md`. The *prompt* is
> the developer's own shell prompt script, which lives outside this repository and is the
> only program that reads the JSON. The *setup check* is the kit's staleness check, which
> every kit skill runs first and which reads FRESH or STALE. The *recorded gates* are the
> lint, format, type-check, test and coverage commands in `.ai-delivery/gates.md`. An ADR
> is an architecture decision record: one decision, its alternatives and its costs.

## Executive summary

The whole feature is two new files: `scratch_notes.py` at the repository root, and
`tests/test_scratch_notes.py`. The script is a set of small pure functions with one thin
command entry, so every counting rule can be tested without starting a process, while a
second group of tests runs the script exactly as the prompt will. Nothing is packaged,
nothing is installed, and no file the setup check tracks is changed.

## Codebase conventions

### Detected stack

From `.ai-delivery/config.md` § Stack; nothing here is re-detected.

- **Language:** Python
- **Framework:** none (`primary_framework: null`)
- **Build tool:** uv
- **Cloud provider:** none (`cloud_provider: null`)
- **Test framework:** pytest, with coverage by pytest-cov
- **Quality and security tools:** ruff, mypy, bandit, pip-audit, gitleaks

### Project structure

- The repository root tracks `.ai-delivery/`, `.gitignore`, `CONTRIBUTING.md`,
  `README.md`, `docs/`, `pyproject.toml` and `uv.lock` (read 2026-10-01).
- It has no Python source outside `.ai-delivery/`, no `src/` directory, no `tests/`
  directory, no CI configuration and no entry point.
- `pyproject.toml` requires Python 3.11 or newer, declares no runtime dependencies and
  has no build backend, so `uv run` does not install the project itself.

### Established patterns

No product module exists to follow, so the two nearest precedents were analyzed:

1. **`.ai-delivery/features/pull-request-checklist/checks/test_contributing.py`**, the
   largest Python file in the repository. It sets the house style this feature follows:
   - a module docstring that says what the file proves and how to run it
   - small pure functions that take text and return a result
   - compiled regular expressions as module constants with a leading underscore
   - type annotations and a docstring on every public function
   - test functions named for the behaviour, each one arrange, act, assert, with
     adverse cases on inline samples beside the real-file cases
2. **`.ai-delivery/features/cited-source-staleness/fr-015-harness/`**, the only other
   executable code. It is a JavaScript harness kept inside its feature directory. It is
   a precedent for location only, and this feature does not follow it: the requirements
   put the script at the repository root, where the prompt calls it by path.

### Test conventions

- pytest is declared in `pyproject.toml`'s dev group and pinned by `uv.lock`. No pytest
  configuration section exists, and none is added: `conftest.py` and `pytest.ini` are
  tracked by the setup check, so adding either would make it read STALE.
- `uv run pytest` from the root collects nothing today and exits with code 5. It skips
  directories whose names begin with a dot, so the older checks under `.ai-delivery/`
  are not in its default run.
- A test under `tests/` cannot `import scratch_notes`: pytest puts `tests/` on the
  import path, not the repository root, and the project is not installed (checked
  2026-10-01 in a scratch copy: `ModuleNotFoundError`).
- Loading the script by its file location with `importlib` works from `tests/` and
  leaves the import path alone. `--cov=scratch_notes` then measures it (checked
  2026-10-01 in the same scratch copy).
- `.ai-delivery/conventions.md` asks for tests in a top-level `tests/` directory, test
  functions named `test_…`, annotated public signatures, docstrings on public functions
  and modules, and exception classes whose names end in `Error`.

### Quality gates as recorded

The recorded gates name `src/` and `tests/`. `src/` does not exist and this feature does
not create it, so three of them cannot check the script as written:

| Recorded gate | What it does here | What verification runs instead |
|---|---|---|
| `uv run ruff check src/ tests/` | Fails: no `src/` | `uv run ruff check scratch_notes.py tests/` |
| `uv run ruff format --check src/ tests/` | Fails: no `src/` | `uv run ruff format --check scratch_notes.py tests/` |
| `uv run mypy src/` | Fails: no `src/` | `uv run mypy scratch_notes.py tests/` |
| `uv run pytest` | Runs the new tests | The same command, unchanged |
| `uv run pytest --cov=src …` | Measures nothing: "No data to report" (checked 2026-10-01) | `uv run pytest --cov=scratch_notes --cov-branch --cov-report=term-missing` |
| `uv run bandit -r src/ -ll` | Fails: no `src/` | `uv run bandit -ll scratch_notes.py` |

`.ai-delivery/gates.md` is setup's record and is not changed here. The coverage targets
it records, 80% of lines and 70% of branches, apply to the script.

### Migrations

None. The repository has no database or schema.

## Use case and business value

**Who it serves.**
- **The developer, Max Adamsky:** keeps about ten Markdown notes files, one per
  personal project, and reads the plain output in the terminal.
- **The prompt:** reads the JSON on every draw and shows the open count, or `?` when
  the script exits non-zero.

**What changes for them.** One command on a notes file gives an open count that follows
a fixed, tested rule, with fenced code ignored, and lists the headings. The prompt gets
both as one line of JSON. A failure can never look like "nothing open", because every
failure exits non-zero with empty stdout.

**Happy path.** The developer switches into a project. The prompt runs
`python3 scratch_notes.py <notes file> --json` and shows the count. The developer runs
the same command without `--json` and reads the count and the headings.

**Success measures** (requirements § 1).
- The open count equals a hand count on the developer's real notes files, including
  files with fenced code. **This one is unproven when the prototype finishes**: no real
  notes files exist in or near this repository, so the tests use a sample file.
- No grep pattern for open items has been written since the tool shipped.
- The prompt shows a number or `?`, never error text.
- Each call takes under 50 ms, timed end to end the way the prompt calls it.

**Out of scope** (requirements § 2): more than one file per run, listing across
projects, failing a check on the count, a version field in the JSON, an installed
command or any packaging, any change to `pyproject.toml` or `uv.lock`, editing notes
files, colour, watch mode, reading stdin, config files, the prompt script itself,
finding a project's notes file, detecting cloud placeholders, and, since 2026-10-01,
any change to `CONTRIBUTING.md`.

## Discovery answers

| Area | Answer | Source |
|---|---|---|
| Problem | The grep for open items reads `[ ]` as a regular expression, so it matches the wrong lines and the count can't be trusted. | requirements § 1 |
| Users and scale | One person, about ten notes files, one file per call. The prompt calls it once per draw, so hundreds of calls a day. | brief § 2 |
| Load at ten times that | Unchanged. Each call is its own short process on one small file. Interpreter startup, not scanning, sets the time. | brief § 6 |
| Measured today | The Homebrew `python3` (3.14.5) starts in 14 to 16 ms. Importing `re` and `json` adds about 1 ms; `dataclasses`, `typing` and `argparse` together add about 7 ms (measured 2026-10-01, 20 runs each). | this session |
| Integration | The prompt, through stdout, stderr and the exit code. Nothing else: no network, no other process, no shared store. | requirements § 2 |
| Interpreters on this machine | `/opt/homebrew/bin/python3` is 3.14.5, the repository's venv is 3.13.9, and `/usr/bin/python3` is 3.9.6, below the 3.11 floor. | this session |
| Compliance | No personal data is stored or sent. The script reads the developer's own notes and prints headings back to the developer's own terminal. | brief § 2 |
| Timeline | None stated. | — |

## Decisions settled in this phase

Max Adamsky settled five questions on 2026-10-01. They are recorded in the Q&A log as
exchanges 31 to 35 and in `docs/decisions.md`.

1. **No real notes files exist here.** The tests build a representative sample file,
   and the 50 ms timing uses it. The hand-count success measure stays unproven until
   the finished script is run on real files.
2. **The `CONTRIBUTING.md` unit is dropped.** MAX-101 is Canceled with the reason
   "descoped for this release", and FR-014 and FR-015 are descoped. `CONTRIBUTING.md`,
   the setup record and the older checklist checks stay as they are.
3. **Anything, or nothing, may follow `[ ]`.** A bare `- [ ]` and `- [ ]buy milk` both
   count as open.
4. **A file over 1 MiB is refused.** This is the new requirement FR-017. A throwaway
   scan took 29 ms on a 1 MB sample, ~~so the 50 ms limit holds at the largest file
   allowed~~, and the timing uses a sample of that size.
   **[REVISED in MAX-100, 2026-10-02]:** the limit holds for a notes-like file at
   that size, not for every file. See `1c-operations.md`.
5. **A one-line backtick snippet is text.** A line starting with three or more
   backticks opens a fence only when no further backtick follows that opening run.

## Architecture decision

### Chosen approach

Discovery settled the direction (brief § 4 to § 6): one standard-library script, run by
path, plus one test file. This design adds how the script is laid out inside, where its
tests live, and how they reach it.

The script runs five steps in order, each a small function:

1. **Version guard.** Under a Python older than 3.11, stop with an error. The whole
   file must still parse under 3.9, so the guard can run there (checked 2026-10-01
   with `/usr/bin/python3`: a file using postponed annotations parses and the guard
   fires).
2. **Parse the arguments.** Exactly one file and an optional `--json`. This is done by
   hand: `argparse` would add a help screen on stdout, option abbreviations and
   start-up time, none of which the contract wants.
3. **Read the file.** Check that the path is a regular file of at most 1 MiB, read its
   bytes once, decode them as UTF-8 and drop a leading byte-order mark.
4. **Scan the lines.** One pass over the lines keeps the fence state and collects the
   open count and the headings. This step is a pure function: text in, summary out.
5. **Render.** The summary becomes either `open: N` followed by the headings, or one
   line of JSON.

Any step can fail. Every failure is raised as one of a small family of error classes
and caught in one place, which writes one line to stderr and returns a non-zero exit
code. Nothing is written to stdout until the scan has finished without error.

The three units build this in order, in the same two files. MAX-98 creates steps 1 to 4
for the open count and the plain `open: N` line. MAX-99 adds heading collection to
step 4 and heading lines to step 5. MAX-100 adds `--json` to steps 2 and 5.

### Architecture diagram

```
 Developer's terminal                 The prompt (outside this repository)
   python3 scratch_notes.py <file>      /opt/homebrew/bin/python3 scratch_notes.py <file> --json
            │                                        │
            └───────────────────┬────────────────────┘
                                ▼
      scratch_notes.py  (repository root; one short process per call)
      ┌──────────────────────────────────────────────────────────────┐
      │ 1 version guard    Python older than 3.11 ──────────────┐    │
      │ 2 parse arguments  not exactly one file, unknown option ─┤    │
      │ 3 read file        missing, not a regular file, over     │    │
      │                    1 MiB, unreadable, not UTF-8 ─────────┤    │
      │ 4 scan lines       fence state → open items → headings   │    │
      │                    file ends inside a fence ─────────────┤    │
      │ 5 render           plain text, or one line of JSON       │    │
      └──────────────┬───────────────────────────────────────────┼────┘
                     │ success                                   │ any failure
                     ▼                                           ▼
        stdout: the result                         stderr: one line
        exit code 0                                exit code non-zero, stdout empty

      tests/test_scratch_notes.py  (collected by a plain `uv run pytest`)
        rule tests ──────► load scratch_notes.py by file location, call steps 2 to 5
        command tests ───► run scratch_notes.py as a process, check stdout, stderr, exit code
```

### ADR-001: Pure functions behind a thin command entry, tested both ways

**Status:** Accepted, proposed by the prototype orchestrator; Max Adamsky approves it
with the implementation plan.
**Date:** 2026-10-01
**Deciders:** Max Adamsky, the prototype orchestrator

**Context.** The contract the prompt relies on is a process contract: stdout, stderr
and the exit code. The counting rules are text rules with dozens of cases. FR-013 must
be proven even on a machine with no old Python, and the coverage targets need a
measurement. The project rubric also requires that tests exercise the shipped file, and
forbids test code from changing the interpreter's import path.

**Decision.** The script is laid out as importable pure functions, with one entry
function that takes the argument list and returns an exit code. The test file loads the
script by its file location, which changes no import path, and calls those functions
for the rule cases. A second group of tests runs the script as a process for the
contract cases: the standard-library-only run with `python3 -I -S`, the named-pipe
timeout, the old-interpreter run, and stdout, stderr and exit code on success and on
each failure.

**Consequences.**
- **Positive:** every rule case runs in microseconds and is measured for coverage. The
  process contract is proven on the real file, exactly as the prompt calls it. The
  version guard is a function that takes a version, so it is proven with a made-up
  version on any machine.
- **Negative:** two ways of reaching the script live in one test file. The project
  rubric's line that tests reach the code "as an installed distribution" cannot be met,
  because the requirements exclude packaging. Requirements outrank the rubric under
  config's `nfr_precedence`, and the specs name this as an exception so verification
  does not treat it as a silent miss.
- **Risks:** the one line that calls the entry function when the file is run as a
  script is reached only by the process tests, so coverage reports it as missed.

**Alternatives considered.**

| Dimension | A: functions, tested in process and as a process | B: process tests only | C: a package under `src/` with a root wrapper |
|---|---|---|---|
| Replaceability | Strong: the scan can be rewritten behind its signature | Strong: only the process contract is fixed | Adequate: two files to keep in step |
| Cognitive load | Adequate: two test groups in one file | Strong: one kind of test | Weak: a wrapper, a package and a path question |
| Risk isolation | Strong: a rule bug fails a rule test, a contract bug a command test | Adequate: every failure is a process failure, slower to read | Weak: the wrapper must find the package, which `-I -S` makes harder |
| Future flexibility | Strong: an installed command later wraps the same entry function | Weak: no coverage number; FR-013 needs an old Python on the machine | Adequate: nearer to packaging, which the requirements exclude |
| **Verdict** | **Chosen** | Rejected | Rejected: breaks "one script at the root, no packaging" |

### ADR-002: The tests live in `tests/`, inside pytest's default run

**Status:** Accepted, proposed by the prototype orchestrator; Max Adamsky approves it
with the implementation plan.
**Date:** 2026-10-01
**Deciders:** Max Adamsky, the prototype orchestrator

**Context.** The project's conventions put tests in a top-level `tests/` directory, and
the project rubric requires that anything added be reachable from the recorded test
command, `uv run pytest`. The earlier pull request checklist feature kept its checks out
of that run so that item 3 of `CONTRIBUTING.md` stayed true. With MAX-101 dropped,
item 3 is not rewritten.

**Decision.** The one test file is `tests/test_scratch_notes.py`, with no `conftest.py`
and no pytest configuration. A plain `uv run pytest` collects it.

**Consequences.**
- **Positive:** the conventions and the rubric are both met, and `uv run pytest` proves
  the feature with no path to remember.
- **Negative:** once this lands, `uv run pytest` no longer exits with code 5. Item 3's
  rule sentence stays accurate, because it promises the empty result only "until the
  first test module lands". Its example line, which says the command exits with code 5
  "today", is then out of date. Max Adamsky accepted this when dropping MAX-101.
- **Risks:** the recorded lint, format, type-check and coverage gates name `src/`, so
  they do not reach the script. Verification runs the same tools on the two files by
  name, as the table above shows.

**Alternatives considered.** Keeping the tests under the feature directory, outside the
default run, would keep item 3's example true. It was rejected because the requirements
ask for tests that `uv run pytest` runs, and the rubric's reachability item would need
an exception that nothing now justifies. A test file at the repository root beside the
script was rejected because the conventions name `tests/`.

## Core data model

The feature stores no data. Its entities are the values that pass between the five
steps.

```
CommandRequest: what the arguments asked for
├── path: text; the one file to read, exactly as given
└── as_json: true or false; added by MAX-100 together with --json

NotesSummary: what one scan found
├── open_count: whole number, zero or more; lines matching the open-item rule
│   outside fenced code
└── headings: ordered list of text; each heading exactly as written, without its line
    ending or trailing spaces and tabs; added by MAX-99 together with heading collection

FenceState: where the scan is, relative to fenced code
├── marker: a backtick or a tilde; absent when outside a fence
├── length: how many marker characters opened the fence; three or more
└── opened_at: the line number, counted from 1, where the fence opened

Failure: one way a run can fail
├── message: one line of text, without a line ending
└── exit_code: a whole number above zero
```

**Relationships:**
- One CommandRequest leads to exactly one NotesSummary or exactly one Failure.
- A scan holds at most one FenceState at a time: fences do not nest.

**Integrity rules:**
- `open_count` and `headings` come from the same pass over the same bytes, so they can
  never describe two different reads of the file.
- Headings keep file order.
- A scan that ends with a FenceState still open produces a Failure, never a
  NotesSummary.
- A Failure never carries any part of a NotesSummary to stdout.

## Open items this design carries

Max Adamsky owns each of these. None blocks the design.

- **The hand-count success measure is unproven.** Needed before the tool is trusted in
  the prompt: run the finished script on real notes files and bring back any
  disagreement, so it becomes a revision of the requirements and a new test case.
- **Item 3's example line goes out of date when the first test lands.** Needed before
  outside contributors read it: decide in which later release item 3 is rewritten.
- **The recorded gates name a `src/` directory that does not exist.** Needed at the
  next setup re-run: decide whether `.ai-delivery/gates.md` should name the paths that
  do exist.

## Revision history

| Date | Change | Reason | Rework ID |
|------|--------|--------|-----------|
| 2026-10-02 | The 50 ms limit is promised for a notes-like file at the size limit, not for every file the script accepts. | Timing the real script at 1 MiB took at most 33 ms on a notes-like mix, 47 ms with an open item on every line and 165 ms on empty lines only: the time follows the number of lines. Max Adamsky kept the 1 MiB limit and restated the promise. | MAX-100 |

## Next steps

- `1b-contracts.md` defines the command's contract, each function's contract, the error
  taxonomy and the testing strategy.
- `1c-operations.md` covers security, performance against the 50 ms limit, how the
  script reaches the prompt, rollback and risks.

Max Adamsky owns the three open items above; the first is the one that decides whether
the tool can be trusted in the prompt.
