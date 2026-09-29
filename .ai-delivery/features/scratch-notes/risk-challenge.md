# Risk Challenge: scratch-notes — one standard-library script, run by path

**Created:** 2026-09-29
**Source:** single-perspective risk pass (one fresh-context subagent)
**Direction assessed:** A — one standard-library Python script, `scratch_notes.py`, plus one
test file, called by the shell prompt by path from this repository with `python3`

This file records what could go wrong with the chosen direction for scratch-notes, a small
tool that gives one developer a trustworthy open-checklist count and heading list for their
Markdown notes, shown in their shell prompt. It is the input for deciding which risks to
settle in the brief and which to carry as open.

> One careful pass, one perspective — issues surfaced here are real signals, but this is
> not complete coverage.

The risk pass saw only the framing and the chosen direction, and none of the council's
findings. The **Found by** line on each risk notes where it independently re-found something
the council had raised. Those IDs point into `exploration-synthesis.md`:

- `STR` is the stress member, which asked what breaks at 100x scale or under hostile input.
- `OPR` is the operator member, which asked what fails once the tool runs.

Two risks were checkable on this machine. Their **Checked** lines record the result.

---

## Critical Risks (High Impact)

### Prompt-draw startup, not parsing, sets the latency (risk-pass Risk 3)

- **Category:** Technical
- **Description:** On a small notes file, interpreter startup dominates the time, not the
  parsing. The 50 ms criterion times "each call on the largest notes file". But if `python3`
  resolves through a shim such as pyenv's, startup alone can exceed 50 ms before the script
  runs. The prompt draws on every command, so any overshoot is felt constantly.
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation signal:** Measure end-to-end wall time exactly as the prompt invokes the tool,
  warm and cold, inside a project with an active environment, and judge criterion 4 against
  that number.
- **Found by:** risk-pass, independently re-found: STR-1

### Fence handling gives silent miscounts or frequent `?` (risk-pass Risk 4)

- **Category:** Technical
- **Description:** Two failure modes pull against each other.
  - **Too strict:** the rule "an unclosed fence is an error" shows `?` while the developer
    is mid-edit, with a fence opened but not yet closed, in exactly the project being worked
    in.
  - **Too naive:** a fence rule that ignores Markdown's matching rules toggles wrongly and
    inverts counting for the rest of the file, giving a confident wrong number with no `?`.
    The rules at stake: the closing fence must use the same character and be at least as
    long as the opening; fences can sit inside list items; a `~~~` inside a ```` ``` ````
    block is not a fence.
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation signal:** The developer settles the exact fence rules: character, length,
  indented fences, and whether an unclosed fence stays an error while editing. The tests
  include nested, mismatched and in-list fences taken from the real notes files.
- **Found by:** risk-pass, independently re-found: STR-2

---

## Significant Risks

*(Medium impact — worth addressing before requirements)*

### The `python3 -I` test does not prove standard-library-only (risk-pass Risk 1)

- **Category:** Technical
- **Description:** Isolated mode (`-I`) does not remove a virtual environment's own
  site-packages from the import path. Under `uv run pytest`, `python3` is the repository's
  venv interpreter, which already has `markdown-it-py` installed. An accidental import would
  pass the test and then fail in the prompt, where `python3` lacks the package.
- **Checked:** verified on this machine.
  - `uv run python3` resolves to `.venv/bin/python3`.
  - `.venv/bin/python -I -c "import markdown_it"` imports it from `.venv/lib/python3.13/site-packages`.
  - With `-S` added (`-I -S`), and with Homebrew `python3 -I`, the import fails with
    `ModuleNotFoundError`.
- **Likelihood:** High
- **Impact:** Medium
- **Mitigation signal:** The standard-library test runs the script with `-I -S`, or with the
  interpreter the prompt uses, or asserts on `sys.modules`, not with plain `-I` under the
  venv.
- **Found by:** risk-pass

### `python3` on PATH changes when the developer switches projects (risk-pass Risk 2)

- **Category:** Assumption
- **Description:** Switching into a project is also when that project's venv, pyenv version
  file or uv shim becomes active and changes what `python3` means. A project pinned below
  3.11, or the macOS system Python, makes the script fail. The prompt then shows `?` in
  exactly the projects being entered. Nothing enforces the 3.11 floor.
- **Checked:** verified in part. `/usr/bin/python3` on this machine is 3.9.6, below the
  floor. Today `python3` on PATH is Homebrew's 3.14.5, and the repository venv is 3.13.
- **Likelihood:** High
- **Impact:** Medium
- **Mitigation signal:** The developer decides whether the prompt calls a fixed absolute
  interpreter path instead of `python3`. The success check then runs the prompt inside at
  least one project with its own activated environment.
- **Found by:** risk-pass

### The line rule and the hand count may disagree (risk-pass Risk 5)

- **Category:** Assumption
- **Description:** The line rule and the developer's count can part ways in several places:
  - `> - [ ]` items in blockquotes don't match the rule.
  - Indented code blocks and HTML comments do match it.
  - A UTF-8 byte-order mark hides an item or heading on the first line.
  - A non-breaking space after the marker defeats "spaces or tabs".
  - A non-UTF-8 byte raises a decode error, so the prompt shows `?`.
  - Any line starting with `#` outside a fence is listed as a heading, including `#tag` or
    shell-comment lines.
- **Likelihood:** Medium
- **Impact:** Medium
- **Mitigation signal:** Before building, the developer runs the rule by hand against the
  ten real notes files and turns every disagreement into a decided test case.
- **Found by:** risk-pass, independently re-found: STR-2, STR-3, STR-4

### Coupling to the working copy goes beyond branch switches (risk-pass Risk 6)

- **Category:** Organizational
- **Description:** Any of these breaks the prompt in all ten projects at once:
  - a half-edited or broken `scratch_notes.py` on any branch
  - a moved or renamed repository directory

  Developing the tool and using it share one file, with no release step between them. The
  direction accepts `?` on branch switches, but not explicitly on edits in progress.
- **Likelihood:** Medium
- **Impact:** Medium
- **Mitigation signal:** The developer explicitly accepts that editing the tool can break
  every prompt, or chooses a stable path for the prompt to call.
- **Found by:** risk-pass, independently re-found: OPR-6

### Finding each project's notes file has no owner (risk-pass Risk 7)

- **Category:** Scope
- **Description:** The tool takes one path, but the prompt script has to know which file to
  pass for the current project. Nothing says where the ten notes files live or what they are
  called. Without a convention, that logic either sprawls in the prompt script or drifts
  into the tool. Drifting into the tool would reopen the exclusions on multiple files,
  config files and cross-project listing.
- **Likelihood:** Medium
- **Impact:** Medium
- **Mitigation signal:** The developer states the per-project notes-file convention, such as
  a fixed filename at the project root. They also state that "no notes file" is the prompt
  script's job, with its own display.
- **Found by:** risk-pass

---

## Watch Items (Lower priority, worth tracking)

None rated low: every risk the pass raised is medium or high on both likelihood and
impact. The cloud-sync assumption in the next section is the closest thing to a watch item.

---

## Unstated Assumptions

| Assumption | Consequence if Wrong |
|------------|---------------------|
| The prompt script can find each project's notes file through a consistent name or location | The prompt has nothing to pass the tool, and file discovery creeps into the tool against the stated exclusions |
| The developer's hand count is the same thing as the scoped line rule | Criterion 1 ("equals a hand count") fails even when the code is correct, and trust is lost the first time they differ |
| The notes files are local, UTF-8, regular files that open instantly | A cloud-synced file not yet downloaded passes the regular-file check and still blocks, hanging the prompt; another encoding produces `?`. Independently re-found: STR-4 |
| A subprocess on every prompt draw is acceptable in the developer's prompt setup | If the prompt runs segments synchronously, any overshoot is felt on every command. The fix, such as caching or an asynchronous segment, is outside this direction |

---

## Top Concern

A fresh `python3` process on every prompt draw is the weak point, and no success criterion
tests it the way it will actually run. Which interpreter runs changes with the environment
active in the project just entered, and its startup sets the latency. Every failure path
turns into `?` or lag at exactly the moment the tool is meant to help: wrong version, shim
overhead, a missing package, an edit in progress. A prompt segment that is sometimes slow and
sometimes `?` loses trust as fast as the grep count did. The direction pins the parsing rules
carefully but leaves the invocation path as a requirement nothing enforces or checks.

---

## Decisions this surfaced

You, Max Adamsky, as project lead, own each of these. Settle them before the brief, or
carry them into it as open:

1. Whether the prompt calls a fixed absolute interpreter path instead of `python3`
   (Risks 2 and 3).
2. How the standard-library test runs: `-I -S`, or the prompt's own interpreter, rather than
   plain `-I` under the venv (Risk 1).
3. The exact fence rules, and whether an unclosed fence stays an error while you are editing
   (Risk 4).
4. The per-project notes-file convention, and that "no notes file" is the prompt script's
   job (Risk 7).
5. Whether you accept that a broken edit to the script breaks every prompt (Risk 6).
6. How criterion 4 is measured: end to end, as the prompt invokes the tool (Risk 3).
