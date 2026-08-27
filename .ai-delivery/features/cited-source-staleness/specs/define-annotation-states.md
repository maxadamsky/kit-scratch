# Code Spec: Define the four annotation states and what each claims

**Unit:** CDR-10 — Define the four annotation states and what each claims
**Design Reference:** `design/1b-contracts.md` Contracts 1 and 3; ADR-003
**Date:** 2026-08-27
**Target repository:** `/Users/maxdamsky/Projects/ai-delivery-kit` — **not this workspace**

> **Read before starting.** This unit edits a repository that has no `.ai-delivery/` of its
> own. Run `/ai-delivery:setup` there first; without it there are no conventions, gates, or
> rubrics to build against and nothing can be verified. See
> `design/1a-discovery.md` § Scope of this build invocation.

## Implementation Summary

- **Files to Create:** 0
- **Files to Modify:** 2
- **Assertions to Add:** 6 (numbers 16–21 in `design/1b-contracts.md` § Testing strategy)
- **Estimated Complexity:** M

## Codebase Conventions

Read from the kit repository on 2026-08-27.

**File/Function Naming:** scripts kebab-case; functions lowerCamelCase; module constants
`SCREAMING_SNAKE_CASE`. Not exercised by this unit — it edits markdown only.
**Markdown structure:** `artifact-schemas.md` is organised as numbered H2 sections
(`## 1. Shared rules` … `## 10.`) with fenced skeleton blocks inside them. Section numbering
is referenced by path-and-section throughout the kit; **do not renumber sections.**
**Verification framework:** `node:assert` via `ai-delivery/tests/portability-conformance.js`,
run directly with `node`. No runner, no watch, no coverage tool.
**Domain convention — one definition, many copies:** the kit's established pattern for shared
text is a canonical statement in `artifact-schemas.md` plus byte-identical copies in the
consuming skills (the gate stanza works this way). Follow it; do not invent an include
mechanism.

## Technical Context

**Key Gotchas**

- **Section numbers are load-bearing.** Other kit files and this feature's own specs cite
  `§ 1`, `§ 4`, `§ 8`. Adding a section between them breaks those references silently.
- **`ungrounded` is bare on purpose.** No colon, no value. An implementer's instinct to make
  it `ungrounded: true` for uniformity destroys the point — a value there would be a claim,
  and there is nothing to claim. The grammar text must say this, not just show it.
- **The Core Rubric exception survives unchanged.** § 1 currently states that Core Rubric
  items carry no per-item annotation and that any per-item source of any tier fails setup's
  self-check diff. `1-kit` inherits that rule; do not carve an exception for it.
- **"owner ruling" and "kit design" are not sources.** See the enumeration in Task 3 — this
  is the largest and least obvious part of the unit.

**Reusable Utilities:** none — this unit adds no executable behaviour beyond assertions.

**Integration Points:** CDR-11 emits against the § 3/§ 4/§ 5 skeletons this unit edits;
CDR-14 copies the § 8 clause byte-identically; CDR-13 converts existing files onto this
grammar. All three read this unit's output as text.

## Contracts

### The annotation grammar

**Component:** `artifact-schemas.md § 1`, the source-annotation block.

| Element | What it must state | Failure signal |
|---|---|---|
| `read_on: YYYY-MM-DD` | A source was read on that date **and the line follows from it**. Records an event, not a standing verification. | Wording that implies the source still says this |
| `unreachable: YYYY-MM-DD` | A source was fetched on that date and did not resolve. Distinct from both a successful read and from never having a source. | Conflated with `ungrounded` |
| `ungrounded` | There was never an external source. **Bare.** A date here would assert a read that never happened. | Written as a key/value pair |
| *(annotation absent)* | The line was written by a person. **Heuristic, not guaranteed**, and both failure modes named. | Stated as a guarantee, or the failure modes relegated elsewhere |

**Data shape — Annotation:** three slots in a bracketed suffix on the line it vouches for —
a source (repository path, URL, kit file path, or the literal `none`), a tier, and one state
token. The carrier does not change from today's; that is what keeps existing files readable
and hand-edits survivable.

**Failure conditions this section must name once:**
- *Invalid tier × state pairing* — `unreachable:` on a tier with no network fetch, or a date
  on `3-model`. Stated as a matrix, not as prose.
- *Bare kit-written line* — an emitter omitting an annotation. Named as an admitted failure
  mode of the absence rule; nothing detects it.

**State/side effects:** none. Nothing in this unit executes against an annotation.

### The verification run record

Defined in § 1, **never emitted anywhere**. Shape: a date the pass ran, and per item a source
plus one outcome of `checked`, `unreachable`, or `never-grounded`. The section must state
that **absence of the record means no pass has ever run**, and must not cause any code path
to write an empty one.

### The citation clause (§ 8)

The canonical text, quoted verbatim in `design/1b-contracts.md` Contract 3. CDR-14 copies it
into four skills. Assertion 19 asserts all five copies are byte-identical, so **this text is
frozen once written** — treat a later wording change as touching five files.

## Task Breakdown

### Task 1: Replace the § 1 source-annotation block

**Dependencies:** None
**Files:** `ai-delivery/skills/setup/references/artifact-schemas.md` (modify)

Replace the existing `**Source annotation**` block and its tier bullets with the grammar from
`design/1b-contracts.md` Contract 1: the three-slot form, the four states with worked
examples, the six-tier table, and the tier × state matrix.

Preserve verbatim: the Core Rubric exception paragraph, the "Profile authoring constraint"
block, "No pre-written code", and "User edits are decisions". Those are unrelated rules that
happen to live in § 1.

Add, as new prose in the same section: why `source: none` is written rather than the
annotation omitted (it is what makes FR-010's grep criterion meaningful), and the
unannotated-line rule with both admitted failure modes.

### Task 2: Add the `1-kit` tier definition

**Dependencies:** Task 1
**Files:** `ai-delivery/skills/setup/references/artifact-schemas.md` (modify)

`1-kit` — the kit's own methodology and specification files **other than the active delivery
profile**, cited by path. State the boundary against `1-profile` as a path rule so no reader
has to judge: the active profile file is `1-profile`; any other kit file is `1-kit`.

Extend the existing prohibition to cover it: neither tier may be cited as a bare name.
Extend the Core Rubric contamination rule to name `1-kit` alongside `1-profile`.

### Task 3: Re-annotate the § 4 Linear Conventions skeleton

**Dependencies:** Tasks 1, 2
**Files:** `ai-delivery/skills/setup/references/artifact-schemas.md` (modify)

**This is the largest task in the unit and the one most likely to be underestimated.** The
skeleton holds 16 bullets. Counted directly on 2026-08-27:

| Bullets | Current state | Required |
|---|---|---|
| 7 | No annotation at all (#2, #3, #4, #5, #13, #14, #15, #16 — see note) | Add an annotation |
| 4 | `[source: kit design · tier: 1-docs · verified: <date>]` (#1, #10, #11, #12) | Real path + `1-kit` + `read_on:` |
| 5 | `[source: owner ruling · tier: 1-docs · verified: <date>]` (#6, #7, #8, #9) | See below — **this is the open one** |

> Note: the bare set is 7 bullets across 8 positions because two adjacent bare bullets share a
> paragraph in the current file. Count by `- ` prefix at the start of a line, not by paragraph.

**`kit design` bullets.** Each states a rule specified elsewhere in the kit. Cite the file and
section that specifies it, tier `1-kit`, `read_on:` the date the implementer reads it. Do not
carry the old date forward — this is a fresh read by the implementer, not a conversion.

**`owner ruling` bullets — a gap the design did not anticipate, and it needs a decision.**
Five bullets attribute their content to a maintainer's ruling. "owner ruling" is neither a
path nor a URL, and no tier covers a human decision recorded nowhere. The rulings *are*
recorded — a search on 2026-08-27 found the initiative-binding and bound-initiative rulings
discussed across the kit's plan and run-record documents at the repository root.

The rule for this task:
1. Locate the plan or run-record document carrying each ruling and cite it by path, tier
   `1-kit`, `read_on:` the read date.
2. **If no record exists for a ruling, stop and surface it.** The honest fix is to record the
   decision (the kit's own convention is `docs/decisions.md`) and then cite it — not to
   annotate it as `3-model`, which would claim model knowledge for a human decision, and not
   to leave it bare, which would claim human authorship of a kit-written line.

Step 2 is an action for the kit maintainer, not something the implementer decides.

**Bare bullets.** Each states a kit design decision. Same treatment: cite the kit file that
specifies it, tier `1-kit`. Where a bullet is itself the only statement of the rule, that is
case 2 above.

### Task 4: Bring the § 3 and § 5 skeletons onto the grammar

**Dependencies:** Tasks 1, 2
**Files:** `ai-delivery/skills/setup/references/artifact-schemas.md` (modify)

**§ 3 `gates.md`:** the `## Thresholds` example currently shows
`coverage_line: 85 [source: pyproject.toml fail_under · tier: 1-code · verified: 2026-08-02]`
and `coverage_branch: 70 [source: scaffold default, confirmed · tier: 1-docs · verified: …]`.

The second is the defect this feature exists for, in the specification itself: a scaffold
default tiered `1-docs` and stamped with a date. It becomes
`[source: none · tier: 3-model · ungrounded]`. The first becomes `read_on:` with a date.

Every other threshold in the example block is currently unannotated and is a scaffold default
— annotate each `ungrounded`.

**§ 5 `rubrics.md`:** update the schema_version statement to 3 and bring any annotated example
onto the new state tokens. **Do not annotate Core Rubric items** — the exception holds.

### Task 5: Add the § 8 citation clause

**Dependencies:** Task 1
**Files:** `ai-delivery/skills/setup/references/artifact-schemas.md` (modify)

Insert Contract 3's clause into § 8 as a new `**Citing an artifact line in a finding.**` block,
after the existing "Guarantees setup makes" list and before "What skills do on MISSING/STALE".
Do not alter the gate command text, the status vocabulary, or the semantics paragraph — thirteen
skills and a shipped test depend on them.

### Task 6: Add the assertions

**Dependencies:** Tasks 1–5
**Files:** `ai-delivery/tests/portability-conformance.js` (modify)

**Cases** (follow the markdown-assertion pattern at `portability-conformance.js:427`):

- § 1 contains no `verified:` occurrence
- § 1 defines `read_on:`, `unreachable:`, and bare `ungrounded`, and states the absence rule
- § 1's tier table names all six tiers, `1-kit` among them
- § 1 contains the tier × state matrix and `3-model` admits only `ungrounded`
- The § 4 Linear Conventions skeleton has no bullet lacking `[source:`
- § 8 contains the citation clause including its "must not present … as currently verified"
  wording
- No `SKILL.md` in the repository defines a local variant of the grammar (grep for the state
  tokens outside the four skills CDR-14 touches plus `artifact-schemas.md`)
- `read_on` appears in no function name, exported symbol, file name, or fixture path
  (assertion 22 — the substitutability property FR-015 depends on)

Add these as one block in the existing stage-1 style, using the file's `scratch()` /
`removeScratch()` helpers where a fixture is needed. Most are static reads of the shipped
file and need no scratch directory.

## Task Dependency Graph

```
Task 1 (§ 1 grammar)
   ├─→ Task 2 (1-kit tier) ──┬─→ Task 3 (§ 4 skeleton) ──┐
   │                          └─→ Task 4 (§ 3, § 5)  ────┤
   └─→ Task 5 (§ 8 clause) ───────────────────────────────┤
                                                          └─→ Task 6 (assertions)
```

Tasks 3 and 4 are independent of each other and of Task 5.

## Pattern References

**Markdown-contract pattern:** `ai-delivery/skills/setup/references/artifact-schemas.md § 8` —
the existing canonical-statement-plus-copies arrangement for the gate stanza. Imitate its
structure: one authoritative block, explicitly labelled as the thing other files copy.

**Assertion pattern:** `ai-delivery/tests/portability-conformance.js:427` —
`assert.match(setupText, /…/)` over a file read at test time. Imitate the read-then-match
shape and the failure message style.

## Implementation Notes

**Security:** none — this unit adds no executable behaviour and no network path.

**Performance:** none — specification text.

**Deployment:** this unit alone does not warrant a plugin version bump; the bump is the
integration unit's, at release.

**Post-implementation verification:** run the full conformance suite. The nine
`deepStrictEqual(evaluateGate(...))` cases and `runGateClassProof()` must pass **unmodified** —
if either needed editing, something in this unit reached beyond its boundary.

## Final Verification

**Functionality**
- [ ] All eight acceptance criteria in the skeleton met
- [ ] Section numbers unchanged; no section inserted between existing ones
- [ ] `ungrounded` is bare everywhere it appears, and the text says why

**Quality**
- [ ] Core Rubric exception preserved and extended to `1-kit`
- [ ] No bullet in § 4 lacks an annotation
- [ ] No annotation cites a bare name; every `1-kit` and `1-profile` source is a path

**Testing**
- [ ] Assertions 16–22 added and passing
- [ ] Full conformance suite passes with the pre-existing cases unmodified

**Open before merge**
- [ ] **FR-015 has run and its result is recorded.** `read_on` is provisional until then; the
      grammar is not merged before the gate. Owner: kit maintainer.
- [ ] **Any `owner ruling` with no recorded decision has been recorded**, or the maintainer has
      ruled on how to annotate it. Owner: kit maintainer.
