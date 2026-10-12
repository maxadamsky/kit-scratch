# Exploration Synthesis: scratch-notes

**Created:** 2026-09-29
**Synthesis basis:** 5 of 5 mandates examined
**Failed members:** None

Five independent perspectives explored how to give one developer an open-checklist count
they can trust in their shell prompt, plus a heading list, for their personal Markdown
notes. This file composes what each found, attributes every finding to the member that
produced it, and records the checks run to settle the factual claims. The raw responses are
in `council-responses/`; each finding below cites its ID there.

**How to read the IDs.** Each finding's ID names the member that made it, followed by a
number:

| Prefix | Member | What it asked | What it could see |
|---|---|---|---|
| `CON` | Constraint | the smallest change to this repository | the repository (codebase) |
| `PRE` | Precedent | what already exists to adopt | the live web |
| `STR` | Stress | what breaks at 100x scale or under hostile input | the framing only |
| `NUL` | Null | the case for not building it | the framing only |
| `OPR` | Operator | what fails once it runs | the repository's operational setup (codebase) |

Numbering follows each response's own order:

- CON-1 and CON-2 are its two directions.
- PRE-1 to PRE-3 are its three candidates.
- STR-1 to STR-6 are its six failure modes.
- NUL-1 to NUL-4 are the four supporting points of its case, NUL-5 is its alternative, and
  NUL-6 is its steelman.
- OPR-1 to OPR-6 are its six scenarios.

## Coverage

| Mandate question | Examined? |
|---|---|
| Constraint: the smallest change to the existing system that solves this | examined — response |
| Precedent: what already exists that could be adopted instead of building | examined — response |
| Stress: what breaks first at 100x scale or under hostile input | examined — partial: over the 1,000-word cap (1,060 words) |
| Null: the strongest honest case that this should not be built | examined — response |
| Operator: what is missing for the first night on call | examined — partial: over the 1,000-word cap (1,072 words) |

All five mandates ran. Two responses exceeded the word cap; both parsed fully and are
synthesized in full.

## Candidate Directions

This roster deliberately counterweights builder's bias: it generates minimal, adopt and
no-build candidates, never an ambitious purpose-built option. You can propose a direction
the exploration didn't surface.

### A. One standard-library script, run by path (CON-1; core pattern also PRE-3)

`scratch_notes.py` and one test file, with no change to `pyproject.toml` or `uv.lock`:

- It opens the notes file read-only and scans it line by line.
- It counts lines matching `^\s*[-*+] \[ \]` and collects `#` headings, skipping fenced code
  blocks.
- It prints plain text, or JSON when given `--json`.
- Errors go to stderr with exit code 1.
- The prompt calls it directly with `python3`, not through `uv run`.

**Gain:** the least new code, fast, and it turns `uv run pytest` into a real gate for the
first time.
**Cost:** no `scratch-notes` command on your PATH, and item 3 of `CONTRIBUTING.md`, which
still says the test run finds nothing, needs updating.

**Bearing findings:**

- **OPR-6.** The prompt runs whatever branch this repository has checked out. Its
  `live-proof-*` branches change often, so the tool would change with them.
- **CON-1's own risk.** `markdown-it-py` is already installed in `.venv`, so a Markdown
  parser could be imported by accident. A test running the script with `python3 -I`, which
  ignores the project's packages, would catch that.
- **STR-1.** Startup cost on each prompt draw.

### B. The same code, installed as a `scratch-notes` command (CON-2)

This is A's code, packaged into `src/scratch_notes/` and registered as a command in
`pyproject.toml`, with a build backend added.

**Gain:** a real command. If the install is a fixed copy, it no longer changes when this
repository's branch changes, which addresses OPR-6.
**Cost:** a build backend (arguably a new build-time dependency), churn in `uv.lock`, and a
choice between `uv run` on every prompt draw or hard-coding the `.venv/bin` path.

**Bearing findings:** STR-1 (startup cost) and OPR-6 (partly mitigated).

### C. Adopt mdq, an existing Markdown query tool (PRE-1; mq, PRE-2, as a weaker variant)

mdq is a separately installed Rust binary. Its `- [ ]` selector picks out open checklist
items, and it can output JSON. A small wrapper script would produce the count and heading
list.

**Gain:** a real Markdown parser, so it handles nesting and code fences.
**Cost:**

- It breaks your "standard library only, no new dependency" constraint.
- It needs two calls per prompt draw.
- Its counting follows Markdown's structure rather than your line-by-line rule, so it can
  disagree with a hand count.
- It has one maintainer.
- PRE-2 found no documented way for mq to select open checklist items at all.

**Bearing findings:** STR-1 (two processes per prompt draw) and OPR-4 (a change in output
shape breaks the prompt script).

### D. A correct grep pattern and no tool (PRE-3, recalled; checked below)

Replace your grep with the anchored pattern `^\s*[-*+]\s+\[ \]`.

**Gain:** no build at all.
**Cost:**

- No JSON and no headings from the same command.
- It still counts lines inside code fences.
- It is still a hand-written pattern, which your success signal says you want to stop
  writing.

The Blind-Spot Ledger records a check of this pattern.

### E. Do not build: fix the grep and check it against a hand count first (NUL-1 to NUL-5)

Null argues that the untrustworthy count is a regex quoting mistake, not something missing:
typed as a regular expression, the `[ ]` in `- [ ]` matches one space, not an empty
checkbox. Null's alternative is one diagnostic sitting:

- Run a corrected grep.
- Compare it with a hand count on two or three real notes files.
- Settle on one checkbox style.

Build nothing unless the counts still disagree. The Factual disputes below show part of this
case verified and part refuted. You must explicitly accept or decline this candidate.

### Findings that apply to every build candidate

A, B and C all have to survive these:

| Finding | What it says |
|---|---|
| STR-2 | Text that only looks like a checkbox, such as a `- [ ]` inside a code block, or a shell `#` comment read as a heading, skews the count. An unclosed code fence silently drops everything after it. |
| STR-3 | Which near-misses count is undefined: `- []`, `- [  ]`, tabs, a non-breaking space, `[X]` and `[-]`. |
| STR-4 | A FIFO, `/dev/zero`, or a cloud placeholder file makes the prompt hang rather than error. |
| STR-5 | Reading while the editor is saving shows a false 0 for one prompt draw. |
| STR-6 | Control characters in heading text can corrupt the terminal. A prompt script that pulls the count out of the JSON with grep or sed can be fooled. |
| OPR-1 | A wrong count is silent, and nothing can diagnose it: there are no line numbers and no version in the output. |
| OPR-2 | Errors that are hidden by design look exactly like "no notes file". |
| OPR-3 | There is no off switch or timeout for a prompt that stalls. |
| OPR-4 | The JSON has no schema version, and no test covers the prompt script. |
| OPR-5 | A change to a notes file would be unrecoverable. |

## Tensions

### Factual disputes

- **Was the wrong count a grep quoting bug?** Null says the untrustworthy count comes from
  quoting (NUL-1, framing-only), against the framing's claim that grep cannot be trusted.
  **Adjudicated: NUL-1's diagnosis is verified.** I ran an 8-line sample through the system
  grep (`/usr/bin/grep`, BSD 2.6.0) and through ugrep 7.8.4:
  - `grep -e '- [ ]'` matched only the two lines with two spaces after the dash, one of them
    the checked `-  [x]`. It missed every normally spaced open item. That is exactly the
    symptom in the framing.
  - Typed without `-e`, `grep '- [ ]'` fails outright with "invalid option", because the
    pattern starts with `-`.
- **Would fixed-string grep be enough?** NUL-5 says fixed-string matching or escaped
  brackets makes the count literal. **Adjudicated: refuted as a fix for the framing's rule.**
  On the same sample, `grep -F -e '- [ ]'` found 2 of the 5 open items. It missed `* [ ]`,
  `+ [ ]` and the double-spaced `-  [ ]`. The anchored ERE from PRE-3 found all 5, and
  correctly excluded the numbered item and both checked items.
- **Does `uv run` make startup too slow?** STR-1 (framing-only) and CON-1 (codebase) against
  no counter-claim. **Adjudicated.** Timed three runs each on this machine:
  - bare `python3` (Python 3.14.5, Homebrew): 0.01–0.03 s
  - `.venv/bin/python`: 0.01 s
  - `uv run`: 0.58 s on the first run, then 0.03 s

  Startup is tens of milliseconds, as claimed. `uv run` roughly doubles the warm cost and
  can take over half a second on a cold or syncing run.

### Priority tensions (for you to decide in direction setting)

- **Build or not build.** CON-1 (codebase) says build the smallest tested script. NUL-1 to
  NUL-5 (framing-only) say fix the quoting and stop.
  - The check above shows grep's miscount was a quoting error. It also shows that the one
    grep fix Null names, fixed-string matching, does not reproduce your rule.
  - Only a line-anchored pattern does. PRE-3 and CON-1 both describe that pattern, and CON-1
    wraps it in a tested tool with JSON output.
  - Building gets you JSON, headings and a rule held in tests. Not building gets you zero
    code to maintain, but a pattern you keep by hand.
- **Where the prompt runs the tool from.** CON-1 (codebase) runs it by path from this
  working copy: least surface, fastest. OPR-6 (codebase) and CON-2 (codebase) run a fixed,
  installed copy. The first is simplest. The second stops your prompt changing whenever this
  repository's `live-proof-*` branches change.
- **Silent errors or a visible failure marker.** Your framing constraint, which CON-1 honours
  (errors to stderr, nothing in the prompt), against OPR-2, OPR-1 and OPR-4 (codebase): a
  visible marker in the prompt such as `?`, plus a version stamp in the JSON.
  - Silence keeps the prompt clean.
  - A marker means "broken" never looks like "nothing open".
  - The marker would be printed by your prompt script, not the tool, so it need not break
    the "errors never print into the prompt" constraint. You decide whether it does.
- **Standard library only, or adopt mdq.** Your framing constraint and CON-1, against PRE-1
  (web: fetched). PRE-1 asks directly whether that constraint stands.
- **What a hand count counts inside code fences.** The framing's rule is line-based and says
  nothing about code blocks. The findings split three ways:
  - CON-1 (codebase) and STR-2 (framing-only) say a `- [ ]` inside a code fence must not
    count, or the count will not match a hand count.
  - PRE-1 (web) notes that mdq already skips fences, while PRE-3's plain pattern does not.
  - STR-2 adds that fence tracking fails in the other direction on an unclosed fence.

  This is a definition you set, not a fact to check.

## Convergences

- **Don't call the tool through `uv run` on every prompt draw.** CON-1 (codebase) and STR-1
  (framing-only). Convergent across disjoint evidence: this raises attention, not
  confidence.
- **Code fences are the main threat to the count matching a hand count.** CON-1's risk
  (codebase), STR-2 (framing-only) and PRE-1 (web: fetched, on mdq's parser skipping
  fences). Convergent across disjoint evidence: this raises attention, not confidence.
- **The counting rule and output shape must be pinned down before building.** CON-1
  (codebase) says to fix the JSON field names and the heading definition in tests. STR-3
  (framing-only) says to set the near-miss rule first. Convergent across disjoint evidence:
  this raises attention, not confidence.
- **A hang, not an error, is the prompt failure nothing catches.** STR-4 (framing-only) says
  a blocked read never raises. OPR-3 (codebase) says no timeout or off switch exists.
  Convergent across disjoint evidence: this raises attention, not confidence.

"Must never change a notes file" (OPR-5) is consistent with the framing, which already says
it. It is an echo, not a convergence.

## Answers by Mandate

- **Constraint (codebase).** The repository has no Python source, no build system and no
  entry point, so the smallest build is one standard-library file plus one test file, called
  as `python3 scratch_notes.py --json`.
  - Strongest statement: the fence rule and the rule that `[x]` is not open are what make
    the count trustworthy. The size budget belongs in the edge-case tests, not in
    infrastructure.
  - It names three follow-ups:
    - Max Adamsky should settle the JSON field names and the heading definition.
    - Whoever lands the change updates item 3 of `CONTRIBUTING.md`.
    - Whoever lands it adds a `python3 -I` test, which fails if the script uses anything
      outside the standard library.
- **Precedent (web).** mdq comes closest: fetched — https://github.com/yshavit/mdq. It
  breaks the standard-library rule, needs a wrapper, and counts by Markdown structure, which
  may differ from your line rule.
  - mq has no documented way to select open checklist items: fetched —
    https://github.com/harehare/mq.
  - The anchored-regex pattern (PRE-3) is recalled and unverified by the member, but I
    checked it; see the ledger.
  - Nothing found delivers the whole output directly. Strongest statement: adopting mdq is a
    trade, not a clean win.
- **Stress (framing-only).** Trust in the count breaks first, not speed:
  - Code fences, blockquotes and spacing variants silently produce a wrong number.
  - Speed breaks second, on per-call startup and `uv run`, not on file size.

  Strongest statement: decide which near-miss checkbox forms count, and how the prompt calls
  the tool without `uv run`.
- **Null (framing-only).** The pain is a mis-typed grep, not a missing tool. The scope of one
  file per call already removes the speed complaint. The prompt display is a want, not a
  pain, and it is what drives every hard constraint.
  - Strongest statement: do not build a tool to route around a quoting mistake until the
    corrected command has been checked against a hand count.
  - Steelman (NUL-6): hand-kept patterns drift, and a small tested tool may be the cheapest
    way to keep the count permanently right.
- **Operator (codebase).** The repository has no CI, no logging, and no gate that has ever
  run. Hidden errors combined with a count trusted without checking means every failure is
  silent.
  - The first-night page is the count vanishing from every prompt after a branch switch
    here, with nothing recording why.
  - Strongest statement: decide on a visible failure marker, a version stamp in the JSON,
    and a fixed installed copy.

## Blind-Spot Ledger

| Assertion | By | Status |
|---|---|---|
| Typed as a regular expression, `[ ]` in `- [ ]` matches one space, so grep miscounts on spacing | NUL-1 (framing-only) | verified: the sample run matched only the two double-spaced lines, including the checked `-  [x]`, and missed every normally spaced open item. Same result on BSD grep 2.6.0 and ugrep 7.8.4. |
| Fixed-string grep, or escaped brackets, gives a trustworthy count | NUL-5 (framing-only) | refuted: `grep -F -e '- [ ]'` found 2 of 5 open items on the sample, missing `* [ ]`, `+ [ ]` and the double-spaced `-  [ ]` |
| The anchored pattern `^\s*[-*+]\s+\[ \]` gives the framing's count | PRE-3 (recalled, so no evidence class) | verified on the 8-line sample: 5 of 5 open items found, numbered and checked items excluded. Code-fence lines not tested; the member itself says they still count. |
| A CPython cold start takes tens of milliseconds, and `uv run` adds more | STR-1 (framing-only) | verified: `python3` took 0.01–0.03 s; `uv run` took 0.58 s cold and 0.03 s warm |
| `json.dumps` escapes control characters in heading text | STR-6 (framing-only) | verified: `json.dumps` turned `\x1b` into `\u001b` |
| Editors that save by truncating and rewriting cause a transient empty read | STR-5 (framing-only) | asserted, unverifiable under its diet; depends on the editor |
| A FIFO or `/dev/zero` as the notes path blocks the read or exhausts memory | STR-4 (framing-only) | asserted, unverifiable under its diet; not tested |
| `markdown-it-py` is installed in `.venv` through `rich` and pip-audit, at `uv.lock` lines 607 and 1012 | CON-1 (codebase) | verified in substance, one detail wrong: line 607 is `markdown-it-py`, `rich` depends on it at line 1016 (not 1012), pip-audit depends on `rich`, and `.venv` contains `markdown_it` |
| `python3` on PATH may be older than 3.11 | CON-1 (codebase) | refuted for now: `python3` is `/opt/homebrew/bin/python3`, version 3.14.5 |
| No CI; gates never run; Build gate `unavailable` | OPR-6 (codebase) | verified: `config.md` has `ci_system: null`; `gates.md` says no verify run has executed and marks Build `unavailable` |
| This repository's `live-proof-*` branches change often | OPR-6 (codebase) | verified in part: the current branch is `live-proof-3.0.1`. How often it changes was not measured. |
| `uv run pytest` exits 5 with "no tests ran" today | CON-1, OPR-4 (codebase) | verified: `CONTRIBUTING.md` lines 17 and 19 say so |
| mdq's `- [ ]` selector and `--output json` | PRE-1 (web) | within its diet (the selector came from a search snippet, JSON from a fetched page); not re-checked here |

**What no member could see.** All three evidence classes ran (codebase, web, framing-only).
Outside every diet:

- your actual notes files: how you really write checkboxes, and whether they contain code
  fences
- your shell prompt script and shell config, which live outside this repository
- your editor's save behaviour

The first of these is the evidence that would settle the code-fence and near-miss
questions.

## Decisions this synthesis surfaced

You, Max Adamsky, as project lead, own every one of these decisions:

1. Whether to accept or decline candidate E, do not build.
2. Which candidate to take forward, if not E.
3. How the prompt runs the tool: by path from this working copy, or as a fixed installed
   copy.
4. Whether a visible failure marker and a version stamp are wanted, alongside silent
   errors.
5. Whether the standard-library-only rule stands.
6. What counts inside code fences, and which near-miss checkbox forms count.

Decisions 1 and 2 are made in direction setting. Decisions 3 to 6 can be settled there or
carried into the brief as open.

## Chosen Direction

**Direction:** A — one standard-library Python script, `scratch_notes.py`, plus one test
file, called by the shell prompt by path from this repository with `python3` (CON-1).
**Rationale:** The tool stays small, and A is the smallest option that still gives a count
the developer can trust, the headings and JSON. Grep gives no JSON or headings, an installed
command adds a build step that isn't needed, and mdq breaks the standard-library rule.

**Scope (MVP):**
- Command: `python3 scratch_notes.py <file> [--json]`, one file per run, read-only.
- Open item: any indentation (spaces or tabs), then `-`, `*` or `+`, then one or more spaces
  or tabs, then exactly `[ ]`.
- Not open: `[x]`, `[X]` and `[-]`. Not a checkbox at all: `- []`, `- [  ]` and `-[ ]`.
  Numbered items don't count. CRLF line endings are accepted.
- Headings: lines starting with `#` to `######`, shown as written with their `#` marks.
  Underlined (setext) headings don't count.
- Lines inside fenced code blocks (```` ``` ```` or `~~~`) count as neither open items nor
  headings. An unclosed fence is an error.
- Output: plain text by default; with `--json`, `{"open": N, "headings": [...]}`, each
  heading a string as written with its `#` marks.
- Errors go to stderr with a non-zero exit, and nothing is printed into the prompt. The
  developer's prompt script shows `?` on a non-zero exit.

**Explicitly excluded:** more than one file per run, listing across projects, failing a
check on the count, a version field in the JSON, an installed command, editing notes, colour,
watch mode, reading stdin, and any config file.

**Success criteria:**
1. The open count equals a hand count on the developer's real notes files, including ones
   with fenced code.
2. No grep pattern for open items has been written since the tool shipped.
3. The prompt shows a number or `?`, never error text.
4. Each call takes under 50 ms on the developer's largest notes file, measured end to end
   the way the prompt invokes it (settled after the risk challenge).

**Constraints:**
- A test running the script with `python3 -I -S` proves it uses only the standard library
  (plain `-I` still sees the venv's packages; settled after the risk challenge).
  `markdown-it-py` is already installed in this repository's environment as a dependency of
  a dev tool, so an accidental import would otherwise go unnoticed.
- It runs on the `python3` on PATH, which must be 3.11 or newer (3.14.5 today).
- It only opens regular files. A directory, named pipe or device path is an error with a
  non-zero exit, so the prompt shows `?` rather than hanging.
- Accepted consequence of running by path: a branch of this repository without the script
  makes the prompt show `?`.
- Item 3 of `CONTRIBUTING.md`, which says `uv run pytest` finds no tests, is updated when the
  first test lands.

**Premise challenge:** NUL-1 to NUL-5: the untrustworthy count is a grep quoting mistake, so
fix the pattern and check it against a hand count instead of building — declined: the tool
stays small.

**Resolved trade-offs:**
- Standard library only, or adopt mdq → standard library only — mdq breaks the rule, and A
  already delivers what the developer needs.
- Where the prompt runs the tool from → by path from this working copy — no build step is
  needed; the branch-switch consequence (OPR-6) is accepted and shows as `?`.
- Silent errors, or a visible failure marker → the prompt script shows `?` on a non-zero
  exit, with no version field in the JSON — "broken" never looks like "nothing open", and the
  JSON stays small.
- What counts inside code fences → lines inside ```` ``` ```` and `~~~` fences are skipped
  for both open items and headings, and an unclosed fence is an error — the developer's notes
  sometimes contain fenced code with checkbox or heading lines.
- Which near-miss checkbox forms count (STR-3) → the rule in the scope above, accepted as
  proposed.
