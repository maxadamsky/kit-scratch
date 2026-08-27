# Code Spec: Report grounding age when a finding cites an artifact line

**Unit:** CDR-14 — Report grounding age when a finding cites an artifact line
**Design Reference:** `design/1b-contracts.md` Contract 6, and Contract 3 for the clause text
**Date:** 2026-08-27
**Target repository:** `/Users/maxdamsky/Projects/ai-delivery-kit`

## Implementation Summary

- **Files to Create:** 0
- **Files to Modify:** 5 (four skills, plus the test file)
- **Assertions to Add:** 3
- **Estimated Complexity:** S

The smallest unit in the feature and the one with the widest blast radius in a reader's
experience: it is what makes the grammar visible to someone who never opens an artifact.

## Codebase Conventions

**One definition, many copies.** The kit's established pattern for shared text: a canonical
statement in `artifact-schemas.md`, copied byte-identically into each consuming skill. The
gate stanza already works exactly this way — `§ 8` says so in its own words: *"This is the
canonical statement; the gate stanza in each skill's SKILL.md copies it."* Follow it. Do not
invent an include mechanism, and do not paraphrase per skill.
**Skill structure:** each of the four is an H2-sectioned `SKILL.md`. Their output sections are
named differently and the insertion anchor differs per file (see Task 2).
**Verification Framework:** `node:assert` in `ai-delivery/tests/portability-conformance.js`.

## Technical Context

**Key Gotchas**

- **Byte-identical means byte-identical.** Assertion 19 compares all five copies. A trailing
  space, a smart quote, or a rewrapped line fails it. Copy, do not retype.
- **The clause is frozen once CDR-10 writes it.** Changing the wording later touches five
  files. Treat CDR-10's § 8 text as the source and this unit as pure propagation.
- **Inputs do not change.** All four skills already read `conventions.md` and `rubrics.md` on a
  FRESH gate. This unit changes what a *finding says*, not what the skill reads. An
  implementer who starts editing gate stanzas has gone out of bounds.
- **Nothing parses an annotation.** The skill reads the artifact as text, as it already does,
  and repeats the grounding the line itself records. No regex over annotations, no helper
  function, no new script.

**Reusable Utilities:** none.

**Integration Points:** consumes CDR-10's § 8 clause. Publishes nothing.

## Contracts

**Component:** the findings output of `critique`, `verify`, `fix`, and `tidy`.

| Cited line's state | What the finding must say | Failure signal |
|---|---|---|
| `read_on: <date>` | The date that line's source was read | Presenting it as currently verified, or omitting the date |
| `ungrounded` | The line has no source | Citing it as a project standard |
| `unreachable: <date>` | The source did not resolve, and on what date | Silently treating it as grounded |
| *(no annotation)* | Nothing special — a human wrote it, which is already the strongest grounding a convention can have | Treating absence as a defect |

The last row matters and is easy to get backwards. An unannotated line is a team decision
someone typed; it does not need a grounding statement and must not be flagged as missing one.

**Worked shape** (from `design/1b-contracts.md` Contract 6):

```
Handlers must return typed errors rather than raising.
  — conventions.md, source read 2026-08-27 (src/api/handlers.py)

Branch coverage below the 70% threshold.
  — gates.md, ungrounded: this threshold is a scaffold default with no source
```

The second example is the behaviour change worth understanding before implementing. Under
today's grammar that threshold reads `verified: 2026-08-12`, and a finding cites it as a
verified project standard. Under this contract the finding says the number was invented —
which it was — and the reader weighs the finding accordingly.

**Failure conditions:** none new. A finding that cannot determine a cited line's state says so
rather than guessing, and the natural cause is an artifact predating the grammar, which
CDR-12's advisory already names.

**State/side effects:** none.

## Pre-Implementation Assertions

**Pattern file:** `ai-delivery/tests/portability-conformance.js:427` — read the skill text,
match the required instruction. For the byte-identity case, read all five files and compare the
extracted clause strings directly rather than matching a pattern five times.

**Cases**
- Each of the four skills contains the citation clause, and all four match `artifact-schemas.md`
  § 8's copy byte-for-byte
- No skill file in the repository defines a local variant of the annotation grammar — grep for
  the state tokens outside `artifact-schemas.md` and these four skills
- The four skills' gate stanzas are unchanged (compare against the shipped stanza text; this
  is a negative assertion guarding the boundary)

**Integration scenario** — exercised by the integration unit:

| Scenario | Steps | Expected outcome |
|---|---|---|
| Ungrounded citation | Run critique against a repository whose coverage threshold is `ungrounded`, on code below it | The finding says the threshold has no source, not that it is a verified standard |

## Task Breakdown

### Task 1: Add the assertions (test-first)

**Dependencies:** None
**Files:** `ai-delivery/tests/portability-conformance.js` (modify)

Write the byte-identity assertion so its failure message names *which* copy diverged. Five-way
identity failures are otherwise slow to diagnose.

### Task 2: Insert the clause into the four skills

**Dependencies:** Task 1, and CDR-10's § 8 text
**Files:**
- `ai-delivery/skills/critique/SKILL.md` — into `## Review Output Format` (line ~151), which is
  where the finding's shape is specified
- `ai-delivery/skills/verify/SKILL.md` — into `## Quality Standards` (line ~376), whose Quality
  Gate bullet already requires deviations be "cited to specific `rubrics.md` items"; the clause
  states how that citation reports grounding
- `ai-delivery/skills/fix/SKILL.md` — into `## Project Standards` (line ~183), where the skill
  already establishes that it reads `conventions.md` and `rubrics.md`
- `ai-delivery/skills/tidy/SKILL.md` — into `## Output Format` (line ~340)

Line numbers are as of 2026-08-27 and are a starting point, not an anchor — locate the section
by heading.

Copy the clause verbatim from § 8. Do not adapt its wording to each skill's voice; the
byte-identity assertion is what keeps four copies from becoming four dialects.

### Task 3: Confirm the boundary

**Dependencies:** Task 2
**Files:** none — a verification step

Confirm by diff that nothing else in the four files changed: no gate stanza, no input list, no
review dimension. This unit adds one block to each of four files and nothing else.

## Task Dependency Graph

```
Task 1 (assertions, test-first) ──→ Task 2 (insert ×4) ──→ Task 3 (boundary check)
```

## Pattern References

**Copy pattern:** `ai-delivery/skills/setup/references/artifact-schemas.md § 8` and any skill's
`## Setup Gate` section — the kit's existing canonical-statement-plus-copies arrangement.
Imitate it exactly.

**Assertion pattern:** `ai-delivery/tests/portability-conformance.js:427`.

## Implementation Notes

**Security, performance, deployment:** none. Four markdown insertions.

**Post-implementation verification.** Diff each of the four files; each shows exactly one added
block. Run the byte-identity assertion.

## Final Verification

**Functionality**
- [ ] All six acceptance criteria in the skeleton met
- [ ] An unannotated line is not flagged as missing grounding

**Quality**
- [ ] All five copies byte-identical
- [ ] No local variant of the grammar defined anywhere
- [ ] No gate stanza, input list, or review dimension touched

**Testing**
- [ ] Three assertions added and passing
- [ ] Full conformance suite passes with pre-existing cases unmodified

**Open before merge**
- [ ] **FR-015 has run**, since the clause names the read field. Owner: kit maintainer.
