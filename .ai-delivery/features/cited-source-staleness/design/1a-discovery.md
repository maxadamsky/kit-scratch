# Honest source annotations: discovery and core design

**Feature:** cited-source-staleness
**Phase:** 1A — Discovery, Architecture, Core Data Model
**Date:** 2026-08-27
**Profile:** software (of config: software)
**Requirements:** `.ai-delivery/features/cited-source-staleness/requirements.md` v1.0 (approved 2026-08-12)

---

## Executive Summary

Every artifact the kit generates stamps its lines with `verified: <date>` — a claim of
standing verification that nothing in the kit performs or re-checks. This design replaces
that single field with a three-token vocabulary that records only what actually happened
(a source was read, a fetch failed, or there was never a source), makes an unannotated
line mean human authorship, and adds one offline reader so an artifact written under the
old vocabulary announces itself instead of being silently misread.

Nothing here fetches, schedules, or gates. The entire mechanism is text a reader can
interpret inside one file with no network and no knowledge of the kit.

---

## Scope of this build invocation

This invocation produces **design and specifications only** — Phases 1A, 1B, 1C, unit
confirmation, and per-unit specs. It writes no production code.

The reason is a stack contradiction, surfaced and decided at Phase 1A:

- The requirements' § 8 names the files this feature changes — `skills/setup/references/artifact-schemas.md`, `scripts/setup-runtime.js`, `skills/setup/SKILL.md`, and four review skill files. All of them live in `/Users/maxdamsky/Projects/ai-delivery-kit`, a Node-and-markdown repository.
- The setup record governing this build is **kit-scratch's**, which records `languages: [python]`, `test_frameworks: [pytest]`, `greenfield: true`. `docs/decisions.md` states that stack was chosen rather than detected, "because the repository was empty."
- The kit repository has no `.ai-delivery/` of its own, so no conventions, gates, or rubrics describe the code this feature actually touches.

Implementation is therefore deferred to the kit repository, after setup has run there. The
specifications this build produces are written against the real kit files, which were read
directly during this phase.

---

## Codebase Conventions

Read from `/Users/maxdamsky/Projects/ai-delivery-kit` on 2026-08-27 — the repository this
design targets, not the workspace this session runs in.

### Detected stack

| Field | Value | Source |
|---|---|---|
| Language | JavaScript (Node, CommonJS, `'use strict'`) | kit repo `scripts/`, `hooks/`, `tests/` |
| Framework | None — Node standard library only, zero runtime dependencies | `scripts/setup-runtime.js` requires only `crypto`, `fs`, `path` |
| Build tool | None | no manifest at the kit root |
| Test harness | `node:assert` via a single executable script, `ai-delivery/tests/portability-conformance.js` | direct read |
| Cloud provider | Not applicable | — |
| Workspace record | `.ai-delivery/config.md` § Stack (kit-scratch: Python/pytest/uv) — **describes a different repository**; cited for completeness, not applicable here | Setup Gate |

### Established patterns

- **Specification files are the product.** The kit's substance is markdown that agents read: `SKILL.md` files, `references/*.md`, `profiles/*.md`. Executable code exists only where markdown cannot carry the behaviour — two hooks, two scripts, one test file.
- **Offline, single-line matching.** `provenanceMatches()` in `scripts/setup-runtime.js:44` reads a file, splits on `/\r?\n/`, and tests exact full-line membership. It wraps the read in `try/catch` and returns `false` on any failure rather than throwing. Every reader this feature adds follows that shape.
- **Failure is a return value, never an exception.** `fingerprintIsFresh` returns `false` for a malformed digest line, a missing file, or a path escaping the root. Errors surface only from `main()`, which writes to stderr and sets `process.exitCode = 1`.
- **Portability is a hard constraint, and it is tested.** `AGENTS.md` and the artifact-schemas "Profile authoring constraint" both forbid shell commands and shell-syntax assumptions outside Node runtimes. `tests/portability-conformance.js` asserts this across all thirteen gate-using skills.
- **User edits are decisions.** Setup never overwrites; re-runs diff-and-propose. An edited line acquires `1-code` standing.

### Naming and file organisation

- Scripts are kebab-case (`setup-runtime.js`, `path-guard.js`, `legibility-check.js`).
- Functions are lowerCamelCase; module-level constants are `SCREAMING_SNAKE_CASE`.
- Each script exports a named object at the bottom and guards `require.main === module`.
- Subcommands are dispatched by a `parseCli`/`main` pair with explicit `if (command === …)` branches.

### Test conventions

One test file, run directly with `node`. It uses `assert`, temporary directories via
`fs.mkdtempSync`, and a `scratch()`/`removeScratch()` pair for isolation. There is no test
runner, no watch mode, and no coverage tool. A new behaviour is proven by adding assertions
to this file.

**Consequence for this feature:** the profile's *Test-first meaning* still applies —
assertions are written before the behaviour — but the artifact is a block of assertions
appended to `portability-conformance.js`, not a new per-unit test file.

---

## Use Case & Business Value

The case this design serves is the **inheritor**: someone opens `conventions.md` in a
repository they did not set up, and every line reads equally authoritative. They cannot tell
a rule grounded in a live document from one grounded in a URL that 404s, and the person who
ran setup has moved on.

The secondary reader is the one that matters more in volume: **the agent**. It treats
`verified:` as a fact, never follows the link, and reviews work against a rule whose
grounding evaporated. It has no path to noticing.

Four defects are confirmed by direct inspection of artifacts generated on 2026-08-12:

1. `gates.md` stamps `tier: 3-model · verified: 2026-08-12` on coverage thresholds never verified against any source.
2. Eight of the thirteen Linear Conventions bullets in `conventions.md` ship with no annotation at all, so absence cannot currently signal human authorship.
3. `schema_version` is written into every artifact and read by nothing.
4. **New, found during this phase:** `conventions.md` carries `[source: kit design · tier: 1-docs · verified: 2026-08-12]`. "kit design" is neither a path nor a URL, and `1-docs` is defined as "official documentation, actually fetched." The kit has no tier for its own design decisions, so one was borrowed dishonestly. See ADR-003.

---

## Architecture Decision

### Chosen approach: one grammar definition, prose propagation, one mechanical reader

The grammar is defined exactly once, in `artifact-schemas.md § 1`. Setup's generation phase
emits it; four review skills cite it; one Node reader checks only the artifact's declared
`schema_version`, never the annotations themselves.

```
                    artifact-schemas.md § 1
                 ┌────────────────────────────┐
                 │   THE GRAMMAR (Unit 1)     │
                 │   read_on: / unreachable:  │
                 │   ungrounded / absent      │
                 │   + legend + run-record    │
                 │     rule + § 8 clause      │
                 └─────┬──────────────┬───────┘
                       │ emitted by   │ cited by
                       ▼              ▼
        ┌──────────────────────┐   ┌──────────────────────┐
        │ setup/SKILL.md       │   │ critique / verify /  │
        │ Phase 3 research     │   │ fix / tidy SKILL.md  │
        │ Phase 6 generate     │   │      (Unit 5)        │
        │      (Unit 2)        │   └──────────┬───────────┘
        │ Re-run convert       │              │ findings state
        │      (Unit 4)        │              │ grounding age
        └──────────┬───────────┘              │
                   │ writes                   │
                   ▼                          ▼
        ┌───────────────────────────────────────────────┐
        │  .ai-delivery/conventions.md · gates.md ·      │
        │  rubrics.md    (schema_version: 2 · 2 · 3)     │
        └───────────────────────┬───────────────────────┘
                                │ read offline by
                                ▼
                 ┌────────────────────────────┐
                 │ setup-runtime.js (Unit 3)  │
                 │ reads schema_version only  │
                 │ → stderr advisory line     │
                 │ → stdout + exit UNCHANGED  │
                 └────────────────────────────┘
```

The load-bearing property: **nothing in this diagram executes against an annotation.** The
grammar's correctness is carried by text a human or agent reads, which is exactly the
mechanism the requirements' no-central-state and offline-operation constraints permit.

### Alternatives considered

| | A: Prose propagation (chosen) | B: Mechanical annotation validator | C: Structured annotation block |
|---|---|---|---|
| How | Grammar stated once; emitters follow by instruction | A subcommand parses annotations and reports or fails on their state | Annotations move out of inline bullets into a parseable frontmatter block |
| Replaceability | **Strong** — the grammar is one section of one file | Adequate — parser couples to annotation syntax | Weak — every artifact and consumer changes together |
| Cognitive Load | **Strong** — a reader learns it in one section, offline | Adequate — reader must also learn what the checker does | **Weak** — the line and its provenance are no longer adjacent |
| Risk Isolation | **Strong** — a wrong annotation is a wrong line, never an outage | **Weak** — routing a freshness verdict into a gate converts a trust problem into a broken build | Adequate |
| Future Flexibility | Adequate — the deferred classifier can be added later without changing the grammar | Strong — the classifier already exists | Strong — machine-readable from day one |
| Verdict | ✅ **Chosen** | Out of scope by requirement (§ 3) | Rejected — breaks § 6's inline-carrier constraint and hand-edit survivability |

Approach C fails a constraint that is easy to underrate: a person editing a convention
bullet will not go and update a separate block. The annotation has to sit on the line it
vouches for, or the hand-edit survivability requirement is lost on contact.

### ADR-001: Three explicit states plus a heuristic fourth

**Status:** Accepted · **Date:** 2026-08-27 · **Deciders:** kit maintainer

**Context.** `verified: <date>` asserts a standing property. The kit performs a read, once,
at generation. The gap between the two is the whole defect.

**Decision.** Replace the single field with three tokens occupying the same third slot, plus
the absence of an annotation as a fourth, explicitly heuristic state:

- `read_on: YYYY-MM-DD` — a source was read on that date, and the line follows from it.
- `unreachable: YYYY-MM-DD` — a source was fetched on that date and did not resolve.
- `ungrounded` — there was never an external source. **Bare: no colon, no value.**
- *(annotation absent)* — written by a person.

**Consequences.**
- *Positive:* every state records an event that happened. No state asserts a standing property. A reader distinguishes all four offline.
- *Negative:* `ungrounded` breaks the uniform `field: value` shape of the other two. This is deliberate — a value there would be a claim, and there is nothing to claim. The asymmetry is the message.
- *Risk:* the absence state is unenforceable and breaks on invited hand-editing. Named in FR-004 and admitted in the legend rather than solved.

### ADR-002: Report version drift on stderr, leaving the gate contract untouched

**Status:** Accepted · **Date:** 2026-08-27 · **Deciders:** kit maintainer

**Context.** FR-012 requires a consumer that reports when an artifact predates the current
grammar, and requires that it **not** change the preflight gate's blocking verdict. But the
gate's output is a hard contract: `artifact-schemas.md § 8` states both forms "print exactly
`MISSING`, `STALE`, or `FRESH`", thirteen skills branch on that word, and
`tests/portability-conformance.js` asserts it. An extra stdout line breaks all three.

**Decision.** The existing `gate` subcommand gains a schema-version check whose entire output
is **one advisory line on stderr**. `process.stdout` and `process.exitCode` are byte-for-byte
unchanged for every input.

**Consequences.**
- *Positive:* the contract, the thirteen gate stanzas, and the conformance test all hold unmodified. The person at the terminal sees the advisory; a skill parsing stdout does not.
- *Negative:* stderr in this script is currently reserved for genuine errors, so this widens its meaning. The advisory line is prefixed to keep the two distinguishable.
- *Risk:* a caller redirecting stderr to `/dev/null` loses the advisory silently. Accepted — the requirement is to report, not to enforce.

**Alternatives.** A new `schema-report` subcommand: rejected because nothing would call it
without editing all thirteen gate stanzas, which is far outside this feature's stated file
list. A second stdout line: rejected — breaks the § 8 contract and a shipped test.

### ADR-003: A tier for the kit's own specification files — SETTLED IN PHASE 1B

**Status:** Superseded — the maintainer chose a new `1-kit` tier on 2026-08-27, not the
`1-profile` widening this section proposed. The accepted decision, its boundary rule, and its
costs are in `design/1b-contracts.md` § Decisions taken since Phase 1A. This section is kept
for the reasoning that led to it.
**Date:** 2026-08-27 · **Decider:** kit maintainer

**Context.** Defect 4 above. Eight Linear Conventions bullets are kit design decisions with
no external source; one more is mis-tiered `1-docs` with "kit design" as its source. Under
the new grammar these must all carry *some* annotation (FR-010), and none of the five
existing tiers fits: they are not model knowledge (`3-model`), not fetched documentation
(`1-docs`), and not in the workspace repository (`1-code`).

**Proposal.** Redefine `1-profile` from "the active delivery profile's own sections" to "the
kit's own methodology and specification files — profiles, references, and skill contracts —
cited by path." The eight bullets then become
`[source: skills/setup/references/artifact-schemas.md § 4 · tier: 1-profile · read_on: <date>]`,
which is honest: a reader can open that file and check the claim.

**Why not the alternatives.** Adding a sixth tier (`1-kit`) is cleaner but is new vocabulary
the requirements did not authorise (§ 8: "Custom needs: None"). Marking them `ungrounded` is
available and safe but *understates* the truth — these lines are grounded in a file a reader
can open, and calling them ungrounded is the same class of error as the one this feature
exists to fix.

**RESOLVED 2026-08-27.** The maintainer chose the new-tier alternative this section argued
against, accepting that it adds vocabulary the requirements' § 8 declared unnecessary. Phase
1B's § 1 tier definitions are written against `1-kit`.

---

## Core Data Model

The entities here are text shapes, not records. Their fields are positions in a line.

### Annotation

The record attached to one artifact line. Absence of an Annotation is itself meaningful and
is not modelled as an empty Annotation.

```
Annotation
├── source : text        — repo path, URL, kit file path, or the literal `none`
├── tier   : enum        — 1-code | 1-docs | 2-context7 | 1-profile | 3-model
└── state  : State       — read_on(date) | unreachable(date) | ungrounded
```

Serialised form, unchanged in carrier from today — one bracketed suffix on the line it
vouches for:

```
[source: <source> · tier: <tier> · read_on: 2026-08-27]
[source: https://example.invalid/spec · tier: 1-docs · unreachable: 2026-08-27]
[source: none · tier: 3-model · ungrounded]
```

`source: none` is written rather than omitted so that a single grep for `[source:` proves
FR-010's coverage claim across every kit-written line. Every annotation opens with the same
token; only the third slot varies.

### Valid tier × state combinations

Not every pairing is meaningful, and the constraint is load-bearing: `unreachable:` records
a **fetch** that failed, which is only possible for a source reached over the network.

| tier | `read_on:` | `unreachable:` | `ungrounded` |
|---|---|---|---|
| `1-code` — workspace repository | ✓ | — (a vanished path is a deleted file, not a failed fetch) | — |
| `1-docs` — fetched official documentation | ✓ | ✓ | — |
| `2-context7` — community-maintained source | ✓ | ✓ | — |
| `1-profile` — kit's own specification files | ✓ | — (local read) | — |
| `3-model` — model knowledge, incl. scaffold defaults | — | — | ✓ |

The `3-model` row is the direct fix for defect 1: a model-knowledge line can only ever be
`ungrounded`, so `gates.md` can no longer stamp a date on its own invented thresholds.

### Artifact

```
Artifact  (conventions.md · gates.md · rubrics.md)
├── schema_version  : int    — conventions 1→2, gates 1→2, rubrics 2→3
├── generated_on    : date
├── regenerated_on  : date | null
├── legend          : text   — in `## About This File`; states what an annotation
│                              promises, the editor's obligation, and that the
│                              human-authored distinction is heuristic
└── lines           : annotated (kit-written) | unannotated (human-written)
```

Per-artifact current versions live as one constant map in `setup-runtime.js`. The reader
compares declared against current and says nothing when they match.

### VerificationRun — defined, never emitted in this phase

```
VerificationRun
├── ran_on : date
└── items  : [ { source, outcome: checked | unreachable | never-grounded } ]
```

The rule, per FR-006: a verification pass writes an itemised dated record **when it runs**.
**Absence of the record means no pass has ever run.** No current code path emits it, and
nothing in this phase creates an empty one — the section simply does not exist in a generated
artifact. Defining the shape without emitting it is the point: an empty record would be the
kit asserting structure it is not backing, which is the same defect under a new name.

### State transitions

An annotation moves between states only by a deliberate act. Nothing in this design moves one
automatically, and no date is ever advanced without a fresh read.

```
   (new line, source read)          (new line, fetch failed, after 1 retry)
              │                                    │
              ▼                                    ▼
      ┌───────────────┐                    ┌────────────────┐
      │   read_on:    │                    │  unreachable:  │
      └───────┬───────┘                    └────────┬───────┘
              │                                     │
              │ human re-reads source ──────────────┘
              │ (new date)
              │
              │ human judges it no longer grounded
              ▼
      ┌───────────────┐        human deletes the line
      │  ungrounded   │ ─────────────────────────────────▶ (gone)
      └───────────────┘

   Old-grammar conversion (Unit 4, proposed by a setup re-run, never automatic):
      verified: <d>  ─┬─ tiers 1-code/1-docs/2-context7/1-profile ──▶ read_on: <d>   (same date)
                      └─ tier 3-model, scaffold defaults ───────────▶ ungrounded     (date dropped)
```

The conversion preserves the date for grounded tiers because a line that was "verified" on a
date was necessarily *read* on that date — the conversion strictly weakens the claim while
keeping the evidence, so it is not a refresh. For `3-model` the original date recorded a read
that never happened, so it is dropped rather than converted.

---

## Discovery questions and their answers

Answered from the requirements, the risk pass, and direct inspection. Scale, compliance, and
integration questions from the phase guide are recorded as not-applicable with reasons rather
than skipped.

| Question | Answer |
|---|---|
| Expected scale | Not a runtime system. Volume is one generated artifact set per repository, read on every skill run. The read/write asymmetry *is* the problem statement: writes stay at one, reads grow without bound. |
| Request volume, growth, geography | Not applicable — no service, no requests. |
| Data volume | Three markdown files per repository, hundreds of lines each. |
| External services, APIs, events | None. The single existing fetch path (setup's research phase) gains a failure-recording behaviour and no new capability. |
| PII, retention, audit, GDPR | None. Artifacts contain repository paths, public URLs, and dates. |
| Deployment model | Plugin distribution. **A content-only commit reports "already at the latest version"** — the plugin version bump is a named Definition-of-Done stage, not a nicety. |
| Existing similar feature to follow | `provenanceMatches()` (`scripts/setup-runtime.js:44`) — an offline single-line check that already proves the technique. FR-012 names it explicitly. |
| Current data model | The existing three-field annotation, defined in `artifact-schemas.md § 1`. This feature changes its third field only. |
| Migration tooling | None, and none needed. Conversion is a text edit proposed through setup's existing diff-and-propose path. |

---

## Open gates and decisions

**FR-015 — the verb change is an untested bet, and it has not been tested.** The requirement
makes it a merge gate: two versions of the same conventions file, one using `verified:` and
one using `read_on:`, put to a model to classify each line's grounding; if the model does not
distinguish them, the field name is reconsidered before FR-001 merges.

**This gate has not run.** The field name `read_on` is provisional throughout this design and
every artifact downstream of it. Owner: the kit maintainer. Until it runs, treat every
occurrence of `read_on` in this document as a placeholder for "the chosen event verb."

**ADR-003 is settled** — see above. The maintainer chose a new `1-kit` tier on 2026-08-27;
Phase 1B was not blocked in the end.

Requirements Q1 (priority inflation: ten of fifteen FRs marked Urgent, against a 60%
guideline) was owed "before decomposition" and decomposition has already run. It is left as
recorded rather than reopened — the unit-level distribution sits at the guideline, and the
unit is the level at which work is scheduled.

---

## Next Steps

- ~~**Phase 1B — contracts.**~~ Written 2026-08-27 to `design/1b-contracts.md`, once ADR-003 was settled.
- **Phase 1C — operations.** The plugin version bump as a release gate, the FR-009 operator message (which must not embed fetched content), and the six-month audit date.
- **Phase 2 — decomposition.** Confirm the five units in `tracker.md` against the Phase 1B contracts and add the integration unit. Linear was unreachable when this document was written; it is reachable as of 2026-08-27.

---

## Actions this document surfaces

- **Run the FR-015 validation gate, or waive it in writing.** The kit maintainer owns this. The grammar's central choice is untested until they do.
- ~~**Settle ADR-003.**~~ Done 2026-08-27: the maintainer chose a new `1-kit` tier. Carried forward as an obligation to edit the requirements' tier preamble — see `design/1b-contracts.md` § Actions.
- **Run `/ai-delivery:setup` in `/Users/maxdamsky/Projects/ai-delivery-kit`** before any implementation of this feature begins. The developer responsible for that repository owns this.
