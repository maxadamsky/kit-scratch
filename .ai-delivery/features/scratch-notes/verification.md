# Verification record: Scratch notes 3.0.2 live proof

This is the durable record of how scratch-notes was verified: each unit's verdict, the
evidence behind it, and the warnings accepted. It matters because the Linear comments
carry the narrative, but this file is the committed record a later reviewer can read
next to the code.

**Feature directory:** `.ai-delivery/features/scratch-notes/`
**Linear project:** P-MAX-15 Scratch notes 3.0.2 live proof
**Profile:** software

> **Terms used here.** MAX-98 (the open count), MAX-99 (the headings), MAX-100 (the
> `--json` output) and MAX-102 (the integration unit) are Linear issues. FR-001 to FR-017
> are requirement labels in `requirements.md`. The *setup check* is the kit's staleness
> check, which reads FRESH or STALE. A verdict of *pass-with-warnings* means every
> acceptance criterion passed and the verifier recorded non-blocking warnings. ADR-001
> and ADR-002 are the decision records in `design/1a-discovery.md`.

## Unit verdicts

| Unit | Verdict | Tests it added | Rework cycles | Label now |
|---|---|---|---|---|
| MAX-98, Count the open checklist items in a notes file | pass-with-warnings; warnings accepted by Max Adamsky, 2026-10-02 | 122 | 0 | `verified` |
| MAX-99, List the notes file's headings under the count | pass | 36 | 0 | `verified` |
| MAX-100, Give the shell prompt the count and headings as JSON | pass-with-warnings; warnings accepted by Max Adamsky, 2026-10-02 | 50 | 0 | `verified` |

## Evidence, 2026-10-02

Run by the main session from the repository root, with all three units in place.
`uv run` uses the venv's Python 3.13.9.

- **`uv run pytest -rs`:** 208 passed, none failed, none skipped.
- **Coverage of `scratch_notes.py`:** 97%, from 168 statements with 5 missed and 38
  branches with 1 partly taken. The missed lines are the body of `main` and the line
  that calls it, which only the tests that run the script as a process reach. The
  targets are 80% of lines and 70% of branches.
- **`uv run ruff check scratch_notes.py tests/`:** clean.
- **`uv run ruff format --check scratch_notes.py tests/`:** clean.
- **`uv run mypy scratch_notes.py tests/`:** clean.
- **`uv run bandit -ll scratch_notes.py`:** no findings.
- **`/usr/bin/python3 scratch_notes.py README.md`** (Python 3.9.6): exit code 1 and
  `scratch_notes: needs Python 3.11 or newer, running 3.9.6`.
- **Setup check:** FRESH after every batch.
- **Working tree:** `scratch_notes.py` and `tests/test_scratch_notes.py` are the only
  new files outside `.ai-delivery/` and `docs/`.

## Timings for FR-012, 2026-10-02

Recorded with MAX-100's verification. Each figure is one end-to-end call of
`/opt/homebrew/bin/python3 scratch_notes.py <sample> --json` (Python 3.14.5) on the
test suite's notes-like sample of exactly 1,048,576 bytes: 64,071 lines, 12,814 open
items and 6,407 headings.

- **The 20 calls of the recorded run, in ms:** 33.4 32.1 32.9 33.1 32.8 32.6 32.9 32.9
  32.4 32.9 33.0 32.6 32.5 32.8 33.0 32.9 32.8 33.1 33.0 32.7. Slowest: 33.4 ms.
- **Twelve further runs of the timing test, slowest call per run, in ms:** 35.9 33.8
  44.8 34.0 34.1 33.5 34.4 33.9 33.8 33.7 33.6 35.8. All under 50 ms.
- **One failure during the build.** The implementer of MAX-100 saw the timing test fail
  once in about 45 runs of the suite, at a load average of about 3, and did not keep
  that run's timings. It has not recurred in 66 runs since.

Timed after MAX-98 alone was built, at exactly 1 MiB, 20 runs each, slowest run: prose
in 80-character lines 20.5 ms; a notes-like mix 33.0 ms; an open item on every line
47.4 ms; empty lines only 165.3 ms.

## Accepted warnings

Max Adamsky accepted these on 2026-10-02 rather than rework the units.

- **MAX-98:**
  - Invisible characters are typed raw into the files, not written as escapes:
    `scratch_notes.py` line 47 (a byte-order mark), and `tests/test_scratch_notes.py`
    lines 288, 289, 445, 535, 537 and 548 (non-breaking spaces), 766 (a byte-order
    mark), and 724 and 725 (the Unicode line and paragraph separators). If an editor
    normalises lines 724 or 725, those tests keep passing while testing nothing.
  - No test shows that an old Python is reported before a wrong command line.
  - The unreadable-file message is not tested with an awkward path.
- **MAX-100:**
  - The timing test can fail on a busy machine although the script is fast enough.
  - An unreadable file, an old Python, a named pipe and a device were tested in plain
    mode only. The integration unit's failure journey now covers them with `--json`.
  - Three or more `--json` options are reported as "given twice".
  - The test module's opening description changed in more places than the build
    reported.

## Not independently confirmed

Both files were new and untracked while the units were built, so there was no earlier
copy to compare against. These rest on each implementer's report:

- that each unit's tests were written first and failed before the code changed
  (reported: a collection error for MAX-98; 36 failed and 122 passed for MAX-99; 41
  failed and 167 passed for MAX-100)
- that no earlier unit's test was edited by a later unit; the test counts, 122 then 158
  then 208, are consistent with it

A comparison copy of both files was taken before integration, so the same question
about the integration unit can be answered by comparison.

## Approved exceptions

- **ADR-001.** The tests load `scratch_notes.py` by file location and never change the
  import path. The project rubric's line that tests reach the code "as an installed
  distribution" cannot be met, because the requirements exclude packaging, and
  requirements outrank the rubric under config's `nfr_precedence`. Max Adamsky approved
  it with the implementation plan.
- **Recorded gates.** The lint, format, type-check, coverage and security commands in
  `.ai-delivery/gates.md` name `src/`, which does not exist. The same tools ran on
  `scratch_notes.py` and `tests/` by name.
- **The 50 ms limit.** It is promised for a notes-like file at the 1 MiB size limit,
  not for every file the script accepts. Max Adamsky decided this on 2026-10-02
  (`docs/decisions.md`).

## Gate states

The software profile carries no sign-off gate. The setup check has read FRESH
throughout: the feature changes no file that check tracks.

## Integration, MAX-102, 2026-10-02

**Verdict:** the post-integration verifier returned pass-with-warnings, and Max Adamsky
accepted the warnings and closed the prototype with the timing gap below recorded. The
finished script holds together:
- The `--json` run on one sample exits 0 with one line of JSON holding the count and
  the headings.
- The plain run on the same file shows the same count and the same headings in order.
- Every failure the script knows behaves the same in plain mode and with `--json`:
  empty stdout, one line on stderr, exit code 2 for a wrong command line and 1 for the
  rest.

**What integration changed:** 23 test cases appended to `tests/test_scratch_notes.py`:
the prompt's journey, the developer's journey, ten failures in two modes, and the
old-Python run with `--json`. Compared against a copy taken beforehand, the earlier
1,908 lines of the test file are an unchanged prefix of the new 2,207, and
`scratch_notes.py` is byte-identical. Nothing was merged and no stand-in was replaced,
because the units were built directly on one another.

**Evidence, run by the main session:**
- **`uv run pytest -rs`:** 231 passed, none failed, none skipped. Twenty further runs
  of the whole suite back to back: 231 passed each time.
- **Coverage of `scratch_notes.py`:** 97%, unchanged.
- **ruff check, ruff format --check, mypy, bandit:** clean.
- **`gitleaks detect --source .`,** over the 36 commits and again over the working
  tree: no leaks found.
- **`uv run pip-audit`:** no known vulnerabilities.
- **Setup check:** FRESH.
- **The 20 timings, in ms:** 33.4 32.5 32.4 32.0 32.2 32.5 32.1 32.6 32.4 32.0 32.3
  32.3 33.7 33.6 32.8 32.6 32.6 32.8 33.4 32.0. Slowest: 33.7 ms. They are also posted
  on MAX-102.

**The timing gap, open.** FR-012's stated method is 20 calls in a row, and it passes.
Those are warm calls; a prompt draw is one call after a pause. Single calls 1.5 seconds
apart, with `/opt/homebrew/bin/python3`, 12 to 15 calls each:

| What was run | In a row, median | 1.5 s apart, median |
|---|---|---|
| `/usr/bin/true` | 1.6 ms | 7.4 ms |
| The interpreter doing nothing | 14.7 ms | 41.8 ms |
| The interpreter with `-I -S`, doing nothing | 9.8 ms | 32.8 ms |
| The script on a 4 KB notes file, `--json` | 17.0 ms | 46.4 ms, up to 51.4 ms |
| The script on the 1 MiB sample, `--json` | 29.5 to 34.7 ms | mostly 59 to 66 ms, up to 71.5 ms |

Interpreter start-up after a pause is about 42 of the 46 ms, so the script cannot
change it. The figures come from one machine, one spacing and a Python timing harness,
not from the prompt. During integration the suite failed twice on the timing test, each
time on the first of its 20 calls only (51.1 ms and 56.8 ms), which is this cold start
and not machine noise.

**Warnings accepted with the close:**
- The test module's opening description names the three units and does not mention
  the end-to-end journeys.
- The probe for an old system Python is written twice, because integration could only
  append to the test file.

Three actions are open in this record, all Max Adamsky's:
- Time the script in the real shell prompt before trusting the 50 ms success measure.
  If the timing test fails on its first call, keep the timings from the failure
  message; that failure is the cold start, not noise to be re-run away.
- Decide whether a later change replaces the raw invisible characters with escapes.
- Run the finished script on real notes files and compare each count with a hand count.
