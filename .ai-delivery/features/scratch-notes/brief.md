# Discovery Brief: scratch-notes

Build scratch-notes: a small standard-library Python script that reads one Markdown notes
file and reports its open checklist items and its headings, as plain text or as JSON. It
matters because the developer's shell prompt will show that open count every time they
switch projects, and today the grep they use miscounts it, so the number cannot be trusted.

*A discovery brief — the discover skill's handoff artifact.*

**Created:** 2026-09-29
**Topic:** scratch-notes
**Discover Session Status:** Completed
**Project:** P-MAX-15 Scratch notes 3.0.2 live proof — https://linear.app/max-test-workspace/project/scratch-notes-302-live-proof-bd6ecd9d3df9
**Council:** constraint, precedent, stress, null, operator
**Discovery issues:** research: MAX-97 https://linear.app/max-test-workspace/issue/MAX-97/explore-solution-directions-for-scratch-notes-and-write-the-decision

**Reading the finding IDs.** Sections 5, 6, 10 and 11 cite findings from the exploration by
ID. The prefix names the perspective that produced the finding, and the number is its
position in that perspective's response:

| Prefix | Perspective | What it could see |
|---|---|---|
| `CON` | Constraint: the smallest change to this repository | the repository |
| `PRE` | Precedent: existing tools to adopt | the live web |
| `STR` | Stress: what breaks at 100x scale or under hostile input | the framing only |
| `NUL` | Null: the case for not building it | the framing only |
| `OPR` | Operator: what fails once it runs | the repository's operational setup |

The full responses are in `council-responses/`, and the synthesis is
`exploration-synthesis.md`, both in this folder.

---

## 1. Problem Statement

One developer keeps about ten Markdown notes files, one per personal project, and wants to
know how many checklist items are still open the moment they switch into a project. Today
they grep for `- [ ]` and skim headings by eye.

Grep gives the wrong count. Unescaped, the `[ ]` is read as a regular expression, so it
matches double-spaced lines, including checked ones, and misses normally spaced open items.
The count therefore cannot be trusted, and the developer's scripts have no reliable way to
get it at all.

Left alone, the developer keeps opening files to check, or keeps acting on a number that is
wrong.

---

## 2. Who Is Affected

**Primary users:** one developer, who reads the plain output in the terminal.

**Secondary stakeholders:** none. The developer's own shell prompt script is the only
machine consumer of the JSON, and no other tool or person reads these notes.

**Scale:** one person, about ten notes files, one file per call.

---

## 3. The Opportunity

When the developer switches into a project:

- One command on that project's notes file gives an open count they trust, and shows the
  headings straight away.
- The shell prompt reads the `--json` output and shows the open count without the developer
  asking.
- The developer stops hand-writing grep patterns and stops opening files to check.

Nothing fails a check on the count, and nothing lists across projects.

---

## 4. Chosen Direction

**Direction:** One standard-library script plus one test file, run by path with `python3`.

**What it is:**
`scratch_notes.py` sits at this repository's root. The shell prompt calls it by path with
`python3`, not through `uv run`. It opens the notes file read-only and scans it line by line:

- It counts open checklist items under a fixed line rule (section 7).
- It collects `#` headings.
- It skips anything inside fenced code blocks.
- It prints plain text, or `{"open": N, "headings": [...]}` when given `--json`.

One pytest file pins every counting rule as a test case. The change adds no packaging, no
build step, and no change to `pyproject.toml` or `uv.lock`.

**Why this direction:**
The tool stays small, and this is the smallest option that still gives a count the developer
can trust, plus the headings and JSON. Grep gives no JSON or headings. An installed command
adds a build step the developer doesn't need. mdq breaks the standard-library rule.

---

## 5. What Was Considered and Not Chosen

The exploration surfaced these directions. They were considered and set aside for the
reasons noted.

| Direction | Why Not Selected |
|-----------|-----------------|
| The same code installed as a `scratch-notes` command, with a build backend (CON-2) | Adds a build step and lockfile churn the developer doesn't need. Calling it through `uv run` on every prompt draw also adds startup time. |
| Adopt mdq, an existing Rust Markdown query tool (PRE-1; mq, PRE-2, as a weaker variant) | Breaks the standard-library-only rule. Still needs a wrapper and two calls per prompt draw. Counts by Markdown structure rather than the agreed line rule. mq documents no way to select open checklist items. |
| A corrected, anchored grep pattern and no tool (PRE-3) | No JSON and no headings from one command. Still a hand-written pattern, which the success signal says the developer wants to stop writing. Still counts lines inside code fences. |
| Do not build: fix the grep pattern and check it against a hand count first (NUL-1 to NUL-5) | Declined: the tool stays small. |

*Note: "Not chosen" does not mean "wrong" — these may be valid future phases or worth
revisiting if constraints change.*

---

## 6. Key Trade-offs Resolved

These decisions were made during direction setting:

### Standard library only, or adopt mdq

**Options considered:**
- Standard library only (the framing's constraint; CON-1): a script with no dependencies.
- Adopt mdq (PRE-1): an external binary with a real Markdown parser.

**Decision:** Standard library only.

**Rationale:** mdq breaks the rule, and the chosen script already delivers what the developer
needs.

### Where the prompt runs the tool from

**Options considered:**
- By path from this repository's working copy (CON-1): the least code, and the fastest.
- A fixed, installed copy (CON-2, OPR-6): stable across this repository's branch switches.

**Decision:** By path from this working copy.

**Rationale:** No build step is needed. The consequence is accepted: on a branch without the
script, the prompt shows `?`.

### Silent errors, or a visible failure marker

**Options considered:**
- Silent errors (the framing's constraint; CON-1): stderr and a non-zero exit, nothing in
  the prompt.
- A visible marker and a version stamp (OPR-1, OPR-2, OPR-4): the prompt shows that the
  tool failed, and the JSON carries a version field.

**Decision:** The developer's prompt script shows `?` when the tool exits non-zero. The tool
itself still never prints into the prompt. No version field is added.

**Rationale:** A broken tool must never look like "nothing open", and the JSON stays small.

### What counts inside code fences

**Options considered:**
- A plain line rule that counts every matching line (PRE-3).
- Skip lines inside fenced code blocks (CON-1, STR-2; mdq behaves this way).

**Decision:** Lines inside ```` ``` ```` and `~~~` fences count as neither open items nor
headings. An unclosed fence is an error, so the prompt shows `?`.

**Rationale:** The developer's notes sometimes contain fenced code with checkbox or heading
lines.

### Which near-miss checkbox forms count

**Options considered:**
- An unsettled rule, where each implementation picks silently (STR-3).
- A fixed rule, decided before building.

**Decision:** The fixed rule in section 7, accepted as proposed.

**Rationale:** Spacing variants are exactly what broke grep, so the rule has to be explicit
and tested.

### How the standard-library guarantee is tested

**Options considered:**
- Run the script with `python3 -I` (CON-1).
- Run it with `python3 -I -S` (risk pass, Risk 1).

**Decision:** `-I -S`.

**Rationale:** This was checked on this machine. Under `uv run`, `python3` is the
repository's venv, and `-I` alone still imports `markdown_it` from it. With `-S` added, the
import fails as intended.

### How the speed criterion is measured

**Options considered:**
- Time each call on the largest notes file.
- Time it end to end, exactly as the prompt invokes it (risk pass, Risk 3).

**Decision:** End to end, the way the prompt calls it.

**Rationale:** Interpreter startup, not parsing, dominates the time.

---

## 7. Scope Sketch

**MVP — what the first release must include:**

- **Command:** `python3 scratch_notes.py <file> [--json]`, one file per run. The file is only
  ever read.
- **Open item:**
  - any indentation (spaces or tabs)
  - then `-`, `*` or `+`
  - then one or more spaces or tabs
  - then exactly `[ ]`
- **Not open:** `[x]`, `[X]` and `[-]`.
- **Not a checkbox at all:** `- []`, `- [  ]` and `-[ ]`.
- **Numbered items** don't count.
- **Line endings:** CRLF is accepted.
- **Headings:** lines starting with `#` to `######`, shown as written, with their `#` marks.
  Underlined (setext) headings don't count.
- **Fenced code:** lines inside fences (```` ``` ```` or `~~~`) count as neither open items
  nor headings. An unclosed fence is an error.
- **Output:** plain text by default. With `--json`, `{"open": N, "headings": [...]}`, each
  heading a string as written with its `#` marks.
- **Errors:** to stderr, with a non-zero exit. Nothing is printed into the prompt. The
  developer's prompt script shows `?` on a non-zero exit.

**Explicitly excluded from this phase:**

- more than one file per run
- listing across projects
- failing a check on the count
- a version field in the JSON
- an installed command
- editing notes
- colour
- watch mode
- reading stdin
- any config file

*Note: Exclusions are not permanent — they are scope boundaries for this phase.*

---

## 8. Success Criteria

How we will know this was solved:

- The open count equals a hand count on the developer's real notes files, including ones
  with fenced code.
- No grep pattern for open items has been written since the tool shipped.
- The prompt shows a number or `?`, never error text.
- Each call takes under 50 ms on the developer's largest notes file, measured end to end, the
  way the prompt invokes it.

---

## 9. Constraints

- It lives in this repository and uses the existing uv and pytest setup.
- It adds no new dependency: Python standard library only, and no Markdown parser.
- A test runs the script with `python3 -I -S` to prove it uses only the standard library.
  `markdown-it-py` is already installed in this repository's venv, as a dependency of a dev
  tool, so plain `-I` would not catch an accidental import.
- It runs on the `python3` on PATH, which must be 3.11 or newer. Today that is Homebrew's
  3.14.5, and the repository venv is 3.13.
- It must be fast enough for the shell prompt to call on every draw.
- It never prints errors into the prompt. Errors go to stderr with a non-zero exit.
- It opens only regular files. A directory, named pipe or device path is an error with a
  non-zero exit, so the prompt shows `?` rather than hanging.
- It must never change a notes file.
- A consequence accepted by running from the working copy: a branch of this repository
  without the script makes the prompt show `?`.
- Item 3 of `CONTRIBUTING.md`, which says `uv run pytest` finds no tests, is updated when the
  first test lands.

---

## 10. Risks Acknowledged

These are the top risks from the risk challenge: one fresh-context reviewer that saw only the
framing and this direction. It is a single perspective, not complete coverage. The full
inventory is in `risk-challenge.md` in this folder. The Found By column shows where that
reviewer independently re-found something the exploration had already raised.

| Risk | Category | Likelihood | Impact | Mitigation Signal | Found By |
|------|----------|-----------|--------|------------------|----------|
| Prompt-draw startup, not parsing, sets the latency. A version-manager shim can push startup alone past 50 ms. | Technical | Medium | High | Measure end to end as the prompt invokes it (now decided). Choose the interpreter path (open question 1). | risk-pass; STR-1 |
| Fence handling gives silent miscounts, or `?` while a fence is being typed | Technical | Medium | High | Settle the exact fence rules, and test nested, mismatched and in-list fences taken from the real notes (open question 2) | risk-pass; STR-2 |
| The `python3 -I` test does not prove standard-library-only under the venv | Technical | High | Medium | Resolved: the test runs with `-I -S` (checked on this machine) | risk-pass |
| `python3` changes when switching into a project, and `/usr/bin/python3` here is 3.9.6, below the floor | Assumption | High | Medium | Choose between a fixed interpreter path and `python3` (open question 1) | risk-pass |
| The line rule and the developer's hand count may disagree. Examples: blockquoted items, indented code, a byte-order mark, `#tag` lines. | Assumption | Medium | Medium | Run the rule against the ten real notes files before building (open question 5) | risk-pass; STR-2, STR-3, STR-4 |
| A half-edited script, or a moved repository, breaks the prompt in all ten projects | Organizational | Medium | Medium | Accept it explicitly, or give the prompt a stable path to call (open question 4) | risk-pass; OPR-6 |
| Nothing owns how the prompt finds each project's notes file | Scope | Medium | Medium | State the per-project convention, and make "no notes file" the prompt script's job (open question 3) | risk-pass |

---

## 11. Council Insights Summary

**Exploration roster:** constraint, precedent, stress, null, operator (of: constraint,
precedent, stress, null, operator)
**Synthesis basis:** 5 of 5 mandates examined

**Coverage gaps:** None — every configured mandate examined. Two responses, stress and
operator, ran slightly over the 1,000-word cap. Both parsed fully.

**Premise challenge:** NUL-1 to NUL-5: the untrustworthy count is a grep quoting mistake, so
fix the pattern and check it against a hand count instead of building — declined: the tool
stays small.

**Convergences** (cross-diet only — raises attention, never confidence):
- Don't call the tool through `uv run` on every prompt draw: CON-1 (codebase) and STR-1
  (framing only). Timed on this machine: plain `python3` took 0.01–0.03 s, and `uv run` took
  0.58 s cold and 0.03 s warm.
- Code fences are the main threat to the count matching a hand count: CON-1 (codebase), STR-2
  (framing only) and PRE-1 (web, from a page fetched this session).
- The counting rule and output shape must be pinned down before building: CON-1 (codebase)
  and STR-3 (framing only).
- A hang, not an error, is the prompt failure nothing catches: STR-4 (framing only) and OPR-3
  (codebase).

**Worth remembering** (from the Blind-Spot Ledger and Answers by Mandate):
- **Null's diagnosis held; its fix did not.** On an 8-line sample, `grep -e '- [ ]'` matched
  only double-spaced lines, including a checked one, and missed every normally spaced open
  item. Typed without `-e`, the pattern fails outright as an invalid option. Fixed-string
  grep, Null's proposed fix, found only 2 of 5 open items. An anchored pattern found all 5.
  PRE-3 recalled that anchored pattern from memory, not from a source, and it was checked on
  that sample.
- **The operator's point outlives this brief:** hidden errors, combined with a count trusted
  without checking, means every failure is silent unless something visible marks it. The `?`
  marker is the answer chosen here.

---

## 12. Prior Art and Context

- Nothing beyond grep. No other tool has been tried or ruled out by the developer.
- Nothing in this repository does this: it has no Python source, no build system and no
  entry point, and `uv run pytest` currently finds no tests (CON-1, OPR-4).
- The exploration found mdq (https://github.com/yshavit/mdq) as the closest existing tool.
  It was not adopted (section 5).

---

## 13. Open Questions

These questions were still unresolved at the end of discovery. Shape should address them
while generating the requirements.

| Question | Why It Matters | Owner (if known) |
|----------|---------------|-----------------|
| 1. Should the prompt call a fixed absolute interpreter path instead of `python3`? | `python3` changes with the environment active in each project. `/usr/bin/python3` here is 3.9.6, below the 3.11 floor, and a shim adds startup time. | Max Adamsky |
| 2. What are the exact fence rules? Settle which characters and lengths close a fence, whether indented and in-list fences count, and whether an unclosed fence stays an error while it is being typed. | A loose rule gives a confident wrong count. A strict one shows `?` mid-edit in the project being worked in. | Max Adamsky |
| 3. What is the per-project notes-file convention, such as a fixed filename at each project's root? Is "no notes file" the prompt script's job, with its own display? | Without a convention, file-finding logic drifts into the tool and reopens the exclusions on multiple files, config files and cross-project listing. | Max Adamsky |
| 4. Is it accepted that a half-edited or broken `scratch_notes.py`, or a moved repository, breaks the prompt in every project? | The prompt runs the working copy directly, with no release step between development and use. | Max Adamsky |
| 5. Does the agreed line rule match the developer's hand count on all ten real notes files? | Blockquoted items, indented code, HTML comments, a byte-order mark, non-breaking spaces and `#tag` lines are where they could disagree, and success criterion 1 depends on agreement. Each disagreement should become a decided test case. | Max Adamsky |
| 6. Does the developer's prompt run this segment synchronously on every draw, and can a cloud-synced notes file that has not been downloaded occur? | A synchronous segment makes every overshoot felt on every command. A placeholder file can pass the regular-file check and still block while it downloads. | Max Adamsky |

---

## Actions this brief surfaced

Max Adamsky, as project lead, owns each of these:

- **Before shape completes:** answer open questions 1–6.
- **For question 5, before any code is written:** run the agreed line rule against the ten
  real notes files.
- **When discovery is complete:** close the Discovery review gate issue, `MAX-92`, and the
  research issue, `MAX-97`. Research is complete and success measures are written here,
  which is what the gate's criteria require.

---

*Generated by the discover skill. See `.ai-delivery/features/scratch-notes/` for all session
artifacts including raw council responses.*
