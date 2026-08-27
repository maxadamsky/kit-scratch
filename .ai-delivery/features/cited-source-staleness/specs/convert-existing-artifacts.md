# Code Spec: Convert existing artifacts to the new grammar on a re-run

**Unit:** CDR-13 — Convert existing artifacts to the new grammar on a re-run
**Design Reference:** `design/1b-contracts.md` Contract 4; `design/1c-operations.md` § Conversion and backfill strategy
**Date:** 2026-08-27
**Target repository:** `/Users/maxdamsky/Projects/ai-delivery-kit`

## Implementation Summary

- **Files to Create:** 0
- **Files to Modify:** 5 (`SKILL.md`, three `reference-output/` samples, the test file)
- **Assertions to Add:** ~6 conversion-mapping assertions
- **Estimated Complexity:** M

## Codebase Conventions

**Instruction style:** as CDR-11 — numbered phases, obligations not suggestions, tables of
check-and-consequence. The re-run behaviour lives in `## Re-runs and staleness`, a
two-column table plus a short rules list.
**Re-run discipline, already established and not to be weakened:** "Existing artifacts are
standing decisions — including lines the user edited by hand. Diff-and-propose; never silently
clobber. An edit the user made is tier `1-code`."
**Verification Framework:** `node:assert` in `ai-delivery/tests/portability-conformance.js`.

## Technical Context

**Key Gotchas — the first one is a defect in the file this unit edits**

1. **The staleness table currently says the wrong thing.** Its `schema_version` row reads:
   *"Artifact `schema_version` vs current → Regenerate skeletons, carry confirmed content
   forward, **refresh dates**."* Refreshing dates is exactly what FR-013 forbids — it would
   move every date forward without any source being re-read, which is the original defect
   performed at scale by the fix for it. **That row must change**, and it is the single most
   important edit in this unit.
2. **The six-month row also needs updating.** *"Convention `verified:` dates older than
   ~6 months → Offer re-verification"* refers to a field that will no longer exist. It becomes
   the new grammar's read date, and the offer stays exactly as it is — an offer, never forced.
3. **`reference-output/` contradicts the specification today.** All three sample files carry
   `schema_version: 1` and `verified:` dates from 2026-08-02, while `artifact-schemas.md` § 1
   already states rubrics carries 2. It is a stale sample, not a second opinion. Refreshing it
   is in this unit's scope so the repository stops shipping an illustration that contradicts
   the thing it illustrates.
4. **Scale.** A typical generated repository carries ~65 annotations — 41 in `conventions.md`,
   22 in `rubrics.md`, 2 in `gates.md`, measured 2026-08-27. The proposal a user reviews is
   large, so it must be grouped and summarised rather than presented as 65 loose diffs.

**Reusable Utilities:** setup's existing diff-and-propose path — this unit adds a proposal
*source*, not a way to write.

**Integration Points:** consumes CDR-10's grammar and CDR-11's proposal path. Shares
`SKILL.md` with CDR-11, which is why it batches after it.

## Contracts

### The conversion mapping

| Existing | Becomes | Date |
|---|---|---|
| `tier: 1-code · verified: <d>` | `tier: 1-code · read_on: <d>` | preserved |
| `tier: 1-docs · verified: <d>` | `tier: 1-docs · read_on: <d>` | preserved |
| `tier: 2-context7 · verified: <d>` | `tier: 2-context7 · read_on: <d>` | preserved |
| `tier: 1-profile · verified: <d>` | `tier: 1-profile · read_on: <d>` | preserved |
| `tier: 3-model · verified: <d>` | `tier: 3-model · ungrounded` | **dropped** |
| scaffold-default threshold, any tier | `tier: 3-model · ungrounded` | **dropped** |
| `source: kit design` or `source: owner ruling`, any tier | the actual kit file path, `tier: 1-kit`, `read_on:` | preserved |
| no annotation, on a line the kit may have written | *undecidable* — proposed for human attention, never auto-classified | n/a |

**Why grounded tiers keep their date.** A line that was "verified" on a date was necessarily
*read* on that date. The conversion strictly weakens the claim while keeping the evidence, so
it is not a refresh and needs no fresh read. For `3-model` the original date recorded a read
that never happened, so it is dropped rather than converted.

**Failure conditions, named once each:**
- *Undecidable line* — an unannotated line that may be a kit line the old emitter skipped or a
  team decision someone typed. The conversion **says so and leaves the line exactly as it is.**
  It never guesses.
- *Unresolvable kit path* — a `kit design` or `owner ruling` source whose specifying document
  cannot be located. Surfaced for the maintainer, not annotated with a placeholder.

**Two invariants that bound the whole unit:**
1. **No date is ever moved forward.** Assertable mechanically by comparing every date in the
   proposed output against the same annotation's date in the input.
2. **Nothing is applied without a human accepting a diff, and nothing is written outside
   `.ai-delivery/`.** The second half is what makes `git checkout -- .ai-delivery/<file>` the
   entire rollback story.

## Pre-Implementation Assertions

**Pattern file:** `ai-delivery/tests/portability-conformance.js:427` for the instruction
assertions; `runStage1SemanticCases()` for any fixture-based case.

**Cases**
- The staleness table's `schema_version` row no longer says dates are refreshed, and states
  that dates are preserved except where a tier's conversion drops them
- The six-month row refers to the new grammar's read date, and the offer remains an offer
- `SKILL.md` states the full tier-aware mapping, including that `3-model` drops its date
- `SKILL.md` states that an undecidable unannotated line is left untouched and reported
- `SKILL.md` states the conversion is proposed through the existing diff-and-propose path and
  is never automatic
- `reference-output/` files carry the current versions and no `verified:` occurrence

**Integration scenarios** — exercised by the integration unit:

| Scenario | Steps | Expected outcome |
|---|---|---|
| Grounded conversion | Re-run setup against an artifact with `1-code · verified: 2026-08-02` | Proposed as `read_on: 2026-08-02` — same date |
| Model demotion | Re-run against `3-model · verified: 2026-08-02` | Proposed as bare `ungrounded`, date gone |
| Kit-source repair | Re-run against `source: kit design · tier: 1-docs · verified: <d>` | Proposed with a real path and `tier: 1-kit` |
| Undecidable line | Re-run against an unannotated convention bullet | Reported as undecidable; line unchanged |
| No forward dates | Compare every date before and after | No date later than it was |
| Decline | Decline the proposal | Nothing written |

## Task Breakdown

### Task 1: Add the assertions (test-first)

**Dependencies:** None
**Files:** `ai-delivery/tests/portability-conformance.js` (modify)

### Task 2: Fix the staleness table

**Dependencies:** Task 1
**Files:** `ai-delivery/skills/setup/SKILL.md` (modify)

Rewrite the `schema_version` row so it no longer instructs a date refresh. The row's new
consequence: regenerate skeletons, carry confirmed content forward, and **convert annotations
per the tier-aware mapping without advancing any date.**

Update the six-month row to name the new read field. Keep it an offer; the requirements'
criticism of this trigger is that it never forces, and that remains deliberate.

### Task 3: Specify the conversion

**Dependencies:** Task 2
**Files:** `ai-delivery/skills/setup/SKILL.md` (modify)

State the mapping table in the re-run section, including the undecidable case and the two
invariants. State that the conversion runs through the existing diff-and-propose path — do not
introduce a second write path, a flag, or a subcommand.

Add the presentation obligation: a proposal touching ~65 annotations is grouped by artifact
and by conversion kind, with counts, rather than presented as a flat diff list. A proposal a
user cannot read is a proposal they accept without reading, which would defeat the
diff-and-propose guarantee.

### Task 4: Enumerate the kit-source repairs

**Dependencies:** Task 3
**Files:** `ai-delivery/skills/setup/SKILL.md` (modify)

`source: kit design` and `source: owner ruling` name no file, so the replacement path cannot be
derived by transformation. Nine bullets in the § 4 skeleton carry one of these — four `kit
design`, five `owner ruling`, counted 2026-08-27.

CDR-10 fixes the skeleton itself. **This unit's obligation is different:** artifacts already
generated in other people's repositories carry the same nine strings, and the conversion must
map them to the same paths CDR-10 chose. Specify that the mapping is a fixed table copied from
CDR-10's result, not a rule applied at conversion time — a rule cannot recover a path from the
string "kit design".

Where CDR-10 could not find a specifying document for an `owner ruling`, this unit inherits
that gap and reports the line as undecidable rather than inventing a citation.

### Task 5: Refresh `reference-output/`

**Dependencies:** Tasks 3, 4
**Files:** `reference-output/conventions.md`, `reference-output/gates.md`,
`reference-output/rubrics.md` (modify)

Bring all three onto the new grammar and the current versions, applying the mapping by hand.
This doubles as the mapping's first real exercise: if a conversion rule is ambiguous here, it
is ambiguous everywhere.

Do **not** advance the `generated_on` dates. These are samples of what a 2026-08-02 run
produced, converted — not a claim that they were regenerated today.

## Task Dependency Graph

```
Task 1 (assertions, test-first)
   └─→ Task 2 (staleness table) ──→ Task 3 (mapping) ──→ Task 4 (kit-source table)
                                                            └─→ Task 5 (reference-output)
```

## Pattern References

**Instruction pattern:** `ai-delivery/skills/setup/SKILL.md` `## Re-runs and staleness` — a
check/consequence table plus a short rules list. Extend it in place.

**Assertion pattern:** `ai-delivery/tests/portability-conformance.js:427`.

## Implementation Notes

**Security.** None beyond the existing re-run path. No fetching happens during conversion —
conversion is a text transformation on files already in the repository, and adding a re-fetch
would advance dates, which invariant 1 forbids.

**Performance.** Not applicable — an interactive re-run.

**Deployment.** Content-only; the plugin bump is the integration unit's.

**The backfill gap is out of scope and must not be papered over.** A repository whose stack
never changes is never offered a re-run and keeps the old grammar indefinitely. This unit must
not claim, count, or report conversion coverage, and must not add a scheduled or forced
trigger. Recorded as R2 in `design/1c-operations.md`, with CDR-12's advisory as the
compensating signal. Owner: kit maintainer.

**Post-implementation verification.** Take a copy of a real schema-1 `.ai-delivery/`, run the
conversion, and diff. Every date is unchanged or removed; no date is later than it was.

## Final Verification

**Functionality**
- [ ] All eight acceptance criteria in the skeleton met
- [ ] The staleness table no longer instructs a date refresh
- [ ] `reference-output/` matches the specification it illustrates

**Quality**
- [ ] No second write path introduced — the existing diff-and-propose path is the only one
- [ ] Nothing written outside `.ai-delivery/`
- [ ] Undecidable lines reported and left untouched, never guessed

**Testing**
- [ ] Conversion assertions added and passing
- [ ] Full conformance suite passes with pre-existing cases unmodified

**Open before merge**
- [ ] **FR-015 has run.** Owner: kit maintainer.
- [ ] **CDR-10's kit-source path table exists**, or its unresolved entries are known. This unit
      copies it; it cannot derive it.
