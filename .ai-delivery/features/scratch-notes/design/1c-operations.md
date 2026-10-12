# Design operations: Scratch notes 3.0.2 live proof

This document covers what it takes for `scratch_notes.py` to run safely in the
developer's shell prompt: security, speed against the 50 ms limit, how the script
reaches the prompt, rollback, what is watched, and the risks. It matters because the
prompt calls the script on every draw and trusts its count without checking, so a slow,
hanging or silently wrong run is felt in every project.

**Date:** 2026-10-01
**Feature directory:** `.ai-delivery/features/scratch-notes/`
**Builds on:** `design/1a-discovery.md` and `design/1b-contracts.md`

> **Terms used here.** MAX-98, MAX-99 and MAX-100 are the Linear issues for the three
> units: the open count, the headings, and the `--json` output. FR-001 to FR-017 are the
> requirement labels in `requirements.md`, and "question N" is open question N at its
> end. The *prompt* is the developer's own shell prompt script, outside this
> repository. C1 to C4 are the contracts in `1b-contracts.md`. The *setup check* is the
> kit's staleness check, which reads FRESH or STALE. *Ship* is the kit's
> commit-and-pull-request skill.

## Database migration strategy

Not applicable: no data changes. The feature adds one script and one test file, and
stores nothing.

## Security design

- **Authentication and authorization:** not applicable; there is no service. The script
  runs as the developer and can read only what the developer can read. It gains no
  privilege and crosses no account boundary.
- **Input handling.** Two inputs cross into the script, and both are checked before any
  processing:
  - **The arguments.** Exactly one path and one known option are allowed; everything
    else is refused (C1).
  - **The file.** Its type, its size and its encoding are checked before the scan: a
    regular file only, at most 1,048,576 bytes, valid UTF-8 (C3).
- **Injection.** The script builds no command, no query and no markup. The path goes
  only to the operating system's own file calls. It starts no process and evaluates no
  text. JSON is produced by the standard library's encoder, which escapes quotes,
  control characters and everything outside ASCII.
- **Regular expressions.** Each one is applied to a whole line, has no nested
  repetition, and runs on at most 1 MiB of text, so no line can make matching blow up.
- **Bounded resources.** The script reads at most the size limit plus one byte, keeps
  one copy of the text and one list of headings, and closes the file before scanning.
- **Never blocking on a non-file.** A directory, a named pipe, a device or a socket is
  refused from its file type alone, before anything is opened (FR-010).
- **Error output.** A message names the path, in escaped ASCII, and the reason. It
  never carries any of the file's content, so notes text can't leak into a log through
  stderr.
- **Data protection:** the script sends nothing anywhere and writes no file. Headings
  go to the developer's own terminal or prompt.
- **Secrets:** none are read or introduced. The secret-detection gate, gitleaks, runs
  over the change as verification evidence.
- **Static analysis:** bandit runs on `scratch_notes.py` at medium severity and above,
  as the recorded gate does for `src/`.
- **Dependencies:** none are added, so the dependency-scan gate has nothing new to
  audit. The `python3 -I -S` test proves the script needs nothing from the venv.

**Accepted and named, not mitigated:**

- **Control characters in plain mode.** Headings are printed as written (FR-005), so a
  heading holding terminal escape codes reaches the terminal unchanged in plain mode.
  JSON mode escapes them. The files are the developer's own.
- **A swap between the check and the open.** The file type is checked, then the file is
  opened. Something replacing the file with a named pipe in between could still block
  the read. Nothing on a single-user machine does that.
- **A cloud placeholder.** A file that looks regular but has not been downloaded can
  block while it downloads (question 6, accepted in the requirements).

## Performance and scalability

### Expected load

One developer, about ten notes files, one call per prompt draw, so hundreds of short
processes a day and never two that depend on each other. A real notes file is a few
kilobytes.

### Targets

| Measure | Target | Source |
|---|---|---|
| Slowest of 20 consecutive `--json` runs on a notes-like 1 MiB sample, with the prompt's interpreter | Under 50 ms | FR-012, FR-017 |
| Named pipe, directory or device | Refused within the same limit, never a hang | FR-010 |
| Memory | Bounded by the 1 MiB limit | FR-017 |

### What was measured

On this machine, 2026-10-01, with `/opt/homebrew/bin/python3` (3.14.5), 20 runs each:

| What | Fastest | Slowest |
|---|---|---|
| The interpreter starting and doing nothing | 14.2 ms | 15.7 ms |
| The same, importing `re` and `json` | 14.9 ms | 15.6 ms |
| The same, also importing `typing`, `dataclasses` and `argparse` | 21.3 ms | 22.7 ms |
| A throwaway scan of a 20 KB sample, end to end | 16.2 ms | 19.0 ms |
| The same scan of a 1 MB sample | 27.1 ms | 28.9 ms |
| The same scan of a 2 MB sample | 39.0 ms | 41.4 ms |

~~Start-up is about 15 ms and the scan adds about 12 ms per megabyte. At the size limit
the script has roughly 20 ms to spare.~~ The throwaway scan lived in a scratch folder and
is not the implementation; the timing test in C4 measures the real script.

**[REVISED in MAX-100, 2026-10-02]:** the real script, timed after the count unit was
built, at exactly 1 MiB with the same interpreter, 20 runs each:

| A 1 MiB file made of | Lines | Fastest | Slowest |
|---|---|---|---|
| Prose in 80-character lines | 13,273 | 19.8 ms | 20.5 ms |
| A notes-like mix of headings, items, prose and fenced code | 57,211 | 27.4 ms | 33.0 ms |
| An open item on every line | 131,072 | 44.1 ms | 47.4 ms |
| Empty lines only | 1,048,576 | 143.6 ms | 165.3 ms |

A notes-like file of 4 KB took 17.4 to 18.1 ms. The time follows the number of lines,
not the number of bytes. The 50 ms limit therefore holds for a notes-like file at the
size limit, with about 10 ms to spare once headings and JSON are added, and does not
hold for a file made of very short lines. The size limit bounds that case at about
165 ms. Max Adamsky kept the 1 MiB limit knowing this.

### How the design keeps to the limit

- Five standard-library imports and nothing else (C2).
- One read of the file and one pass over its lines.
- No `uv run` and no version-manager shim in the call: the prompt calls a fixed
  interpreter by absolute path (question 1). Discovery timed `uv run` at 0.58 s cold.

### Growth

Ten times the files or ten times the prompt draws changes nothing, because each call is
its own process on one file. Ten times the file size is refused by the size limit
before it can cost more than the bounded time above. What does not scale is outside the script: an interpreter
reached through a shim, or a notes file kept on a slow network drive.

## Deployment strategy

### Where the prototype lands

The prototype's sandbox is the working tree of branch `live-proof-3.0.1`. The
implementers write the two files there and commit nothing. Max Adamsky commits and
opens the pull request at handoff, through ship or by hand. The handoff is a draft pull
request with test evidence in its description.

### Rollout

All at once, with no flag. The script is in use the moment the prompt is pointed at it,
and pointing the prompt at it is Max Adamsky's step, outside this repository. Until
then the script changes nothing for anyone.

### The proof chain

```
MAX-98 built → whole suite and gates on the two files
  → MAX-99 built → whole suite and gates
  → MAX-100 built → whole suite and gates
  → per-unit verification
  → integration: the three journeys on one sample, the timing run recorded,
    the setup check still FRESH
  → handoff: draft pull request with this evidence
  → Build stage: engineering merges
  → Max Adamsky points the prompt at the script and runs it on real notes files
```

There is no CI. Every step before the merge runs locally.

### Constraints on reaching the prompt

1. **The prompt calls the working copy.** On a branch without `scratch_notes.py`, or
   with a half-edited one, the prompt shows `?` in every project (question 4,
   accepted).
2. **The prompt calls a fixed interpreter.** It should be
   `/opt/homebrew/bin/python3`, by absolute path, not `python3` and not `uv run`
   (question 1).
3. **The setup check is unaffected.** The feature adds no `conftest.py`, no
   `pytest.ini` and changes no file the check tracks, so it stays FRESH. Integration
   confirms this by running it.

### Rollback

1. Delete `scratch_notes.py` and `tests/test_scratch_notes.py`, or revert the commit
   that added them.
2. The prompt then shows `?` until Max Adamsky removes the call from the prompt script.

There is no data to restore. A rollback takes minutes.

### Post-deployment checks

- **In prototype:** `uv run pytest` passes; ruff, the format check, mypy and bandit
  pass on the two files by name; coverage of the script meets 80% of lines and 70% of
  branches; the 20 timings are recorded; the setup check reads FRESH.
- **After the prompt is pointed at the script:** the prompt shows a number in a project
  with a notes file, and `?` when the path is wrong. The open count on each real notes
  file equals a hand count.

## Observability

- **Logs:** one line on stderr per failed run, naming the path and the reason. The
  prompt discards stderr, so the way to find out why it shows `?` is to run the same
  command by hand.
- **Metrics and traces:** none. A process that lives for 20 ms has nowhere to send
  them, and the requirements exclude a config file to say where.
- **The alert** is the `?` in the prompt. It appears on every failure, because no
  failure exits 0.
- **Exit codes** tell two kinds of failure apart: 2 for a wrong command line, 1 for
  everything else.
- **The health check** is `uv run pytest`, which includes the timing run on this
  machine.

## Risk assessment

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| The line rule disagrees with a hand count on real notes files | Medium | High | The rule is fixed and tested case by case; real files are checked after the script exists, and each disagreement becomes a test case | Max Adamsky |
| A later unit breaks an earlier one, since all three change the same two files | Medium | Medium | The whole suite and the gates run after each unit; a later unit may extend a function but not change what an earlier one delivered (C2) | The prototype orchestrator, this session |
| ~~The timing test fails on a busy machine although the script is fast enough~~ **[REVISED in MAX-102, 2026-10-02]:** the timing test fails when its first call is a cold one | Medium | Low | A failure on the first call only is the cold start described below, not noise; keep the timings from the failure message | Max Adamsky |
| A prompt draw is a single call after a pause, which is slower than the 20 calls in a row that FR-012 times: about 46 ms on a 4 KB file and about 60 ms at 1 MiB, measured 1.5 seconds apart | High | Medium | Not fixable in the script, since interpreter start-up is about 42 ms of it. Time it in the real prompt; calling the interpreter with `-I -S` saved about 9 ms on a bare start | Max Adamsky |
| A notes file of very short lines near 1 MiB takes up to about 165 ms, over the 50 ms limit | Low | Low | Accepted on 2026-10-02; the size limit bounds it, and a real notes file is a few kilobytes | Max Adamsky |
| The timing test is skipped on a machine without `/opt/homebrew/bin/python3`, so FR-012 is unproven there | Medium | Low | The skip states its reason; the limit is a promise about the prompt's machine, which has that interpreter | Max Adamsky |
| A later edit uses syntax newer than Python 3.9, so an old Python prints a syntax error, not the version message | Medium | Low | The old-Python command test runs wherever `/usr/bin/python3` is older than 3.11, which includes this machine | Whoever edits the script |
| The prompt calls a shim or an old interpreter | Medium | Medium | A fixed absolute path in the prompt script (question 1); an old Python is refused with a message | Max Adamsky |
| A half-edited script breaks the prompt in every project | Medium | Medium | Accepted (question 4); the `?` makes it visible | Max Adamsky |
| Item 3 of `CONTRIBUTING.md` has an out-of-date example once the first test lands, and `.ai-delivery/conventions.md` repeats it | Certain | Low | Accepted when MAX-101 was dropped; rewrite in a later release, followed by a setup re-run | Max Adamsky |
| The recorded lint, format, type-check and coverage gates name `src/`, so they don't reach the script | Certain | Low | Verification runs the same tools on the two files by name; `.ai-delivery/gates.md` is setup's record and is unchanged | Max Adamsky, at a later setup re-run |
| A notes file over 1 MiB shows `?` | Low | Low | The message names the limit; split the file | Max Adamsky |
| A cloud placeholder blocks the read | Low | Medium | Accepted (question 6) | Max Adamsky |
| Terminal escape codes in a heading reach the terminal in plain mode | Low | Low | Accepted; JSON mode escapes them | Max Adamsky |
| A file is swapped for a named pipe between the check and the open | Low | Low | Accepted; nothing on a single-user machine does this | Max Adamsky |

## Revision history

| Date | Change | Reason | Rework ID |
|------|--------|--------|-----------|
| 2026-10-02 | The risk table now says the timing test fails on a cold first call, and adds the gap between calls in a row and calls spaced like prompt draws. | Measured at integration: single calls 1.5 seconds apart took about 46 ms on a 4 KB file against 17 ms in a row. Max Adamsky closed the prototype with the gap recorded. | MAX-102 |
| 2026-10-02 | The 50 ms limit is promised for a notes-like file at the size limit, not for every file the script accepts. | Timing the real script at 1 MiB took at most 33 ms on a notes-like mix, 47 ms with an open item on every line and 165 ms on empty lines only: the time follows the number of lines. Max Adamsky kept the 1 MiB limit and restated the promise. | MAX-100 |

## Final sign-off

- [x] Database migration strategy: not applicable.
- [x] Security reviewed: inputs checked on arrival, no injection path, bounded reads,
  no secrets; three accepted exposures named.
- [x] Performance targets: under 50 ms for a notes-like file at the size limit, with
  measurements showing about 10 ms to spare; slower for files of very short lines,
  bounded at about 165 ms.
- [x] Deployment plan: the sandbox, the proof chain, three constraints and a rollback.
- [x] Observability: the stderr line, the `?` and the two exit codes.
- [x] Risks identified, each with a mitigation and an owner.

Three actions come out of this document, all owned by Max Adamsky. The first is to run
the finished script on real notes files and compare each count with a hand count,
before trusting the number in the prompt. The second is to point the prompt at the
script with `/opt/homebrew/bin/python3` by absolute path. The third is to decide when
item 3 of `CONTRIBUTING.md` is rewritten, and to re-run setup then.
