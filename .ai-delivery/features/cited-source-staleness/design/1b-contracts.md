# Honest source annotations: the contracts

**Feature:** cited-source-staleness
**Phase:** 1B — Detailed Contracts
**Date:** 2026-08-27
**Version:** 1.0
**Profile:** software (of config: software)
**Requirements:** `.ai-delivery/features/cited-source-staleness/requirements.md` v1.0 (approved 2026-08-12)
**Preceded by:** `design/1a-discovery.md`

---

## What this document fixes

This document writes the exact text and signatures the five units emit and read: the
annotation grammar, the legend a reader meets inside the artifact, the clause that makes a
review finding state its grounding, the conversion mapping for artifacts already written,
and the one Node reader that notices an artifact written under an older grammar.

It matters because every one of these is a *contract between units that never run
together*. Setup writes an annotation on one machine in one repository; a review agent reads
it months later somewhere else, with no shared code path and no network. Agreement has to be
carried entirely by text that both sides interpret identically, so the text is the interface,
and imprecision in it is the same class of defect as a wrong function signature.

Contracts here are stated at interface level and carry no code, per the profile's
*Spec contents*. The one executable unit is specified by signature, return shape, and
invariants; its implementation is written in Phase 3 and later.

**Scope reminder, carried from Phase 1A.** This build invocation produces design and
specifications only. The files these contracts govern live in
`/Users/maxdamsky/Projects/ai-delivery-kit`, a Node-and-markdown repository with no
`.ai-delivery/` of its own; the setup record governing this session describes kit-scratch
(Python/pytest). Implementation waits on setup running in the kit repository.

---

## Decisions taken since Phase 1A

Phase 1A closed with two items it recorded as the maintainer's. Both were put to the
maintainer on 2026-08-27 and are recorded here as answered.

### ADR-003 — Add a sixth tier, `1-kit`, for the kit's own specification files

**Status:** Accepted · **Date:** 2026-08-27 · **Decider:** kit maintainer
**Supersedes:** the `1-profile` widening that Phase 1A proposed.

**Context.** Phase 1A's fourth defect: `conventions.md` carries
`[source: kit design · tier: 1-docs · verified: 2026-08-12]`. "kit design" is neither a path
nor a URL, and `1-docs` is defined as documentation *actually fetched*. Eight further Linear
Conventions bullets are kit design decisions carrying no annotation at all. Under FR-010 all
of them must carry one, and none of the five existing tiers fits: they are not model
knowledge, not fetched documentation, and not in the workspace repository.

**Decision.** Add `1-kit` — the kit's own methodology and specification files other than the
active profile, cited by path. `1-profile` keeps its existing meaning unchanged.

**The boundary between the two is decidable by path, and that is deliberate:**

| Cited file | Tier |
|---|---|
| `ai-delivery/skills/setup/profiles/<active profile>.md` | `1-profile` |
| Any other kit file — `references/`, `shared/`, a skill's `SKILL.md` | `1-kit` |

A reader never has to judge which one applies; they look at the path.

**Consequences.**
- *Positive:* the eight bare bullets and the mis-tiered one become
  `[source: ai-delivery/skills/setup/references/artifact-schemas.md § 4 · tier: 1-kit · read_on: <date>]`
  — a claim a reader can check by opening the named file. No existing tier changes meaning,
  so no already-written `1-profile` annotation becomes wrong.
- *Negative, and it is real:* the requirements' § 8 states "Custom needs: None." A sixth tier
  is new vocabulary beyond what the requirements authorised. The maintainer chose it with
  that cost stated. It obliges an edit to the requirements' own "Reading the tier codes"
  preamble, which is listed under Actions below.
- *Risk:* `1-kit` is available to any emitter and could become the tier of convenience for a
  line nobody wants to ground. The mitigation is the same one `1-profile` already relies on —
  the tier requires a path, and a path that does not resolve is visible to any reader.

**Contamination rule, carried across.** `artifact-schemas.md § 5` states that a `1-profile`
source inside the Core Rubric is the contamination signature. `1-kit` inherits that rule
verbatim: Core Rubric items carry no per-item annotation of any tier, and a `1-kit` source
appearing inside Core fails setup's self-check diff exactly as `1-profile` does.

### FR-015 — the verb stays provisional, and the gate runs before implementation

**Status:** Decided · **Date:** 2026-08-27 · **Decider:** kit maintainer

The requirements make the `verified:` → `read_on:` change a merge gate: two versions of the
same conventions file put to a model, which is asked to classify each line's grounding; if it
does not distinguish them, the field name is reconsidered before FR-001 merges. **The gate has
not run.**

The maintainer's decision is to write this document and the Phase 3 specifications with
`read_on` marked provisional throughout, and to run the gate before implementation begins in
the kit repository.

**What "provisional" obliges, concretely.** Every contract below is written so that the verb
is substitutable: `read_on` appears only in the third slot of the annotation, is never part of
a file name, a function name, an exported symbol, or a test-fixture path, and the reader
specified in Contract 5 never matches on it. Changing the verb after the gate runs is a
find-and-replace across the grammar text and the emitters — not a redesign. That property is a
contract in its own right and is asserted in the testing strategy.

---

## Contract 1 — The annotation grammar

**Owner:** Unit 1 (CDR-10) · **Consumers:** Units 2, 4, 5 and every downstream reader
**Location:** `ai-delivery/skills/setup/references/artifact-schemas.md § 1`, replacing the
existing "Source annotation" block.
**Requirements:** FR-001, FR-002, FR-003, FR-004, FR-010

### Serialised form

Three slots, one bracketed suffix on the line it vouches for. The carrier does not change —
that is what keeps existing files readable and hand-edits survivable.

```
[source: <path | URL | none> · tier: <tier> · <state>]
```

The third slot takes exactly one of three tokens:

```
read_on: YYYY-MM-DD      a source was read on that date, and the line follows from it
unreachable: YYYY-MM-DD  a source was fetched on that date and did not resolve
ungrounded               there was never an external source — bare, no colon, no value
```

A fourth state is the **absence** of the whole annotation, and it means the line was written
by a person.

### Worked examples, one per state

```
- Handlers return typed errors rather than raising.
  [source: src/api/handlers.py · tier: 1-code · read_on: 2026-08-27]
- Migrations run forward-only in deploy.
  [source: https://example.invalid/ops-guide · tier: 1-docs · unreachable: 2026-08-27]
- coverage_branch: 70
  [source: none · tier: 3-model · ungrounded]
- We never deploy on a Friday.
```

The fourth line carries no annotation, and under this grammar that is a statement: a person
wrote it.

### Why `source: none` is written rather than the annotation omitted

FR-010's coverage claim is verifiable by grep — every kit-written line contains `[source:`.
If an ungrounded line dropped its annotation instead, the grep would no longer separate
"kit wrote this without a source" from "a human wrote this", and the fourth state would carry
no information. The literal `none` is what makes the absence state meaningful.

### The tiers, with `1-kit` added

| Tier | Means | Cite as |
|---|---|---|
| `1-code` | Read from the workspace repository — code, config, existing docs. Outranks everything. | repository-relative path |
| `1-docs` | Official documentation, actually fetched on the stated date. | URL |
| `2-context7` | Context7 or another community-maintained source; useful, not authoritative. | URL or library identifier |
| `1-profile` | The active delivery profile's own sections. | `ai-delivery/skills/setup/profiles/<profile>.md § <section>` |
| `1-kit` | The kit's own methodology and specification files other than the active profile. | `ai-delivery/…/<file>.md § <section>` |
| `3-model` | Model knowledge, no external grounding. Always advisory. | the literal `none` |

Neither `1-profile` nor `1-kit` may be cited as a bare name: "the ai-delivery setup skill" is
neither a path nor a URL and violates this grammar.

### Which states each tier may take

The constraint is load-bearing, not decorative: `unreachable:` records a **fetch** that
failed, which is only possible for a source reached over a network.

| Tier | `read_on:` | `unreachable:` | `ungrounded` |
|---|---|---|---|
| `1-code` | ✓ | — a vanished path is a deleted file, not a failed fetch | — |
| `1-docs` | ✓ | ✓ | — |
| `2-context7` | ✓ | ✓ | — |
| `1-profile` | ✓ | — local read | — |
| `1-kit` | ✓ | — local read | — |
| `3-model` | — | — | ✓ |

The `3-model` row is the direct fix for Phase 1A's first defect: a model-knowledge line can
only ever be `ungrounded`, so `gates.md` can no longer stamp a date on thresholds it invented.

### The unannotated-line rule, and its two admitted failure modes

An unannotated line signals human authorship. This is **heuristic, not guaranteed**, and the
grammar says so in the same breath rather than in a footnote. It breaks two ways:

1. **Pre-existing files.** An artifact generated before this grammar shipped has unannotated
   kit-written lines. Its `schema_version` is what distinguishes it, which is why Unit 3
   exists.
2. **An emitter that omits.** If a future emitter forgets an annotation, its line becomes
   indistinguishable from a human's. Nothing detects this; the grep in FR-010 is a
   maintainer's check, not an enforced gate.

Stating both is FR-004's acceptance criterion. Neither is solved here, and claiming otherwise
would be the same defect this feature exists to fix.

### The verification run record — stated, never emitted

**Requirement:** FR-006.

A verification pass writes an itemised, dated record **when it runs**. Each item names its
source and one outcome: `checked`, `unreachable`, or `never-grounded`.

**Absence of the record means no pass has ever run.**

No current code path emits this record, and nothing in this feature creates an empty one. An
empty record would be the kit asserting structure it is not backing — the same defect under a
different name. The shape is defined so that a future pass has something to conform to, and
for no other reason.

---

## Contract 2 — The artifact legend

**Owner:** Unit 2 (CDR-11) · **Consumers:** every human and agent that opens an artifact
**Location:** the `## About This File` section of `conventions.md`, `gates.md`, and
`rubrics.md`.
**Requirements:** FR-005

This is the only part of the mechanism a reader meets without being told to look for it, so
it is specified as exact prose rather than as intent. It must be interpretable with no
network, no source catalog, and no knowledge of how the kit works.

```markdown
**Reading the source annotations.** Lines the kit wrote carry a bracketed suffix naming where
their content came from. `read_on:` means someone read that source on that date and this line
follows from it — it is a record of a read, not a promise that the source still says this.
`unreachable:` means the source was fetched on that date and did not resolve. `ungrounded`
means there was never an external source; a date there would assert a read that never
happened. A line with no annotation was written by a person.

This file states no expiry and no policy. Whether a date is old enough to matter is your
judgment. If you distrust a line, re-read its source and update the date, delete the line, or
change it to `ungrounded`.

**If you edit an annotated line's text, update or remove its annotation.** The annotation
vouches for the words next to it; leaving it in place over changed text makes it a false
record.

**The no-annotation rule is a convention, not a guarantee.** A file generated before this
grammar shipped has kit-written lines with no annotation, and an emitter that forgets one
produces a line indistinguishable from yours.
```

Three properties this wording is holding, and each has a corresponding assertion in the
testing strategy:

- It states the **conjunction** FR-005 requires — someone read this source on this date *and
  the line follows from it*. A promise of a read alone would be weaker than the annotation is
  meant to be.
- It states the **editor's obligation** as an instruction to the reader, in the second person,
  because the reader holding the file open is the only party who can honour it.
- It **admits the heuristic** in the legend itself, not only in the grammar file, because a
  reader who never opens `artifact-schemas.md` would otherwise over-trust the absence state.

---

## Contract 3 — The skill citation clause

**Owner:** Unit 1 (CDR-10) writes it; Unit 5 (CDR-14) propagates it
**Location:** `ai-delivery/skills/setup/references/artifact-schemas.md § 8`
**Requirements:** FR-007

`§ 8` is the canonical contract the other thirteen skills copy from. The clause added there is
the single definition; the four review skills carry a copy, and the copy is byte-identical.

```markdown
**Citing an artifact line in a finding.** A finding that rests on a line from
`conventions.md`, `gates.md`, or `rubrics.md` states that line's grounding as the line itself
records it — the date its source was read, or that it is `ungrounded` or `unreachable:`. A
finding must not present a cited line as currently verified: the annotation records a past
read, and nothing in the kit re-checks it.
```

---

## Contract 4 — The conversion mapping

**Owner:** Unit 4 (CDR-13) · **Requirements:** FR-013

Applied only through setup's existing diff-and-propose path on a re-run. Never automatic, and
**no date is ever moved forward.**

| Existing annotation | Becomes | Date |
|---|---|---|
| `tier: 1-code · verified: <d>` | `tier: 1-code · read_on: <d>` | preserved |
| `tier: 1-docs · verified: <d>` | `tier: 1-docs · read_on: <d>` | preserved |
| `tier: 2-context7 · verified: <d>` | `tier: 2-context7 · read_on: <d>` | preserved |
| `tier: 1-profile · verified: <d>` | `tier: 1-profile · read_on: <d>` | preserved |
| `tier: 3-model · verified: <d>` | `tier: 3-model · ungrounded` | **dropped** |
| scaffold-default threshold, any tier | `tier: 3-model · ungrounded` | **dropped** |
| `source: kit design · tier: 1-docs · verified: <d>` | `source: <the actual kit file path> · tier: 1-kit · read_on: <d>` | preserved |
| no annotation, on a line the kit wrote | proposed annotation, tier by inspection | new read date |

**Why grounded tiers keep their date.** A line that was "verified" on a date was necessarily
*read* on that date. Converting the claim strictly weakens it while keeping the evidence, so
it is not a refresh and does not need a fresh read. For `3-model` the original date recorded a
read that never happened, so it is dropped rather than converted.

**The last row is the one that needs a human.** A pre-existing unannotated line cannot be
classified mechanically — it may be a kit line the old emitter skipped, or a team decision
someone typed. The conversion proposes; it never decides. Where the re-run cannot tell, it
says so in the proposal rather than guessing, and an undecided line is left exactly as it is.

**The `kit design` row is not a rename.** `source: kit design` names no file, so the
conversion cannot produce the replacement path by transformation — it must be supplied per
line from the § 4 skeleton the bullet came from. Phase 3 enumerates the nine affected bullets
with their target paths; this is a table of nine specific edits, not a rule.

---

## Contract 5 — The schema version reader

**Owner:** Unit 3 (CDR-12) · **Requirements:** FR-011, FR-012
**Location:** `ai-delivery/scripts/setup-runtime.js`

This is the feature's only executable contract, and it is specified tightly because it sits
next to a frozen one.

### The constraint that shapes it

`ai-delivery/tests/portability-conformance.js` asserts the gate contract in two ways, and both
are load-bearing:

1. Nine cases call `assert.deepStrictEqual(evaluateGate(root), { status, exitCode })`.
   **`deepStrictEqual` means a third key on that return object fails all nine.**
2. `runGateClassProof()` executes all thirteen skills' gate commands and asserts
   `result.stdout.trim()` equals the status word and that exit codes stay 11-blocking /
   2-advisory. It does **not** assert on stderr.

Together these settle the design: `evaluateGate()` is untouchable, and stderr is the only
channel with room. This is ADR-002 from Phase 1A, now grounded in the specific assertions that
force it.

### Signature

```
schemaVersionDrift(rootValue) → Array<{ artifact, declared, current }>
```

- **Input:** the same root string `evaluateGate` takes.
- **Output:** one entry per artifact whose declared version is **below** the current version
  for that artifact, plus one entry per artifact **above** it. Empty array when everything
  matches, when nothing is readable, and in every failure case.
- **Never throws.** Every read is wrapped, and any failure yields `[]`, following
  `provenanceMatches()` (`scripts/setup-runtime.js:44`), which returns `false` rather than
  raising on a missing or unreadable file.
- **Exported by name**, added to the existing `module.exports` object. The test file imports
  by destructuring, so an added export breaks nothing.

### The version map

```
conventions.md → 2      (from 1)
gates.md       → 2      (from 1)
rubrics.md     → 3      (from 2)
```

A module-level `SCREAMING_SNAKE_CASE` constant, matching the file's existing convention.

`config.md` is deliberately absent. It carries values, not source annotations, so this
grammar change does not touch it and bumping its version would assert a change that did not
happen.

**Verified against live artifacts, not against the specification.** `reference-output/` in the
kit repository carries `schema_version: 1` on all three files, which contradicts
`artifact-schemas.md § 1`'s statement that rubrics carries 2. Artifacts generated on
2026-08-12 carry conventions 1, gates 1, rubrics 2 — matching FR-011. `reference-output/` is a
stale sample predating the rubrics bump, and Phase 3 lists refreshing it as part of Unit 4.

### How it reads

A single anchored regex per file — `/^schema_version: (\d+)\r?$/m` — over the file's text.
No frontmatter parser, no YAML dependency, no multi-line state.

**Deviation from `provenanceMatches()`, stated because it is a deviation.** That function
tests exact full-line *membership*, which is sufficient for a known-value check. It is not
sufficient here: membership can only answer "is this file at version N", so a file at
version 3 read by a kit expecting 2 would be reported as predating the grammar, which is
false. Reporting requires the declared number, so the reader captures it. Everything else
about the shape is preserved — one file, one line, offline, failure as a return value.

The `\r?` is not defensive padding: the conformance test already exercises CRLF fixtures.

### ADR-004 — A file with no `schema_version` line is silent

**Status:** Accepted · **Date:** 2026-08-27 · **Decider:** this design

A file whose `schema_version` line is absent or unparseable produces **no entry**.

*Why.* Every real artifact since the frontmatter convention carries the key, so absence means
the file is not a generated artifact — a stub, a hand-made placeholder, or a fragment. The
`§ 8` provenance check already owns the absent-key migration signal. Reporting on absence
would fire on the conformance test's own STALE fixture, which writes a four-line `rubrics.md`
stub, and an advisory that cries wolf during the test suite is one nobody reads in the field.

*Cost, accepted:* an artifact predating frontmatter entirely goes unreported. No such artifact
is known to exist.

### The advisory line

Exactly one line, on stderr, whatever the number of drifted artifacts:

```
ai-delivery setup runtime: advisory: artifacts predate the current annotation grammar — conventions.md (1→2), gates.md (1→2); see ai-delivery/skills/setup/references/artifact-schemas.md § 1
```

An artifact *ahead* of the current version reads `conventions.md (3→2, written by a newer kit)`
in the same list.

The existing error prefix in this file is `ai-delivery setup runtime: `. The advisory extends
it with `advisory: ` so that a person scanning stderr, and any log filter, separates the two
without ambiguity. `process.stdout` and `process.exitCode` are byte-for-byte unchanged for
every input — that is the invariant, and it is asserted directly rather than inferred.

### Call site

Inside `main()`, in the `gate` branch only, **after** `process.stdout.write(result.status + '\n')`
so a caller piping stdout receives its word first, and before `process.exitCode` is set.

It runs for every gate status. On `MISSING` there is no `.ai-delivery/` directory, so the
reader returns `[]` and says nothing without needing a special case. No other subcommand calls
it, and no skill's gate stanza changes.

### What this contract does not do

It does not read, parse, validate, or act on a single annotation. It reads one integer from
one frontmatter line. The grammar's correctness is carried by text that humans and agents
read — routing a freshness verdict into an executable gate is exactly the failure mode the
requirements put out of scope in § 3, because it converts a trust problem into an outage.

---

## Contract 6 — Grounding age in review findings

**Owner:** Unit 5 (CDR-14) · **Requirements:** FR-014
**Location:** `skills/critique/SKILL.md`, `skills/verify/SKILL.md`, `skills/fix/SKILL.md`,
`skills/tidy/SKILL.md`

Each of the four skills already reads `conventions.md` and `rubrics.md` on a FRESH gate. The
change is to their findings output, not to their inputs.

A finding that cites an artifact line states the grounding the line itself records:

```
Handlers must return typed errors rather than raising.
  — conventions.md, source read 2026-08-27 (src/api/handlers.py)

Branch coverage below the 70% threshold.
  — gates.md, ungrounded: this threshold is a scaffold default with no source
```

The second example is the one that changes behaviour. Under today's grammar that threshold
reads `verified: 2026-08-12` and a finding cites it as a verified project standard. Under this
contract the finding says the number was invented, which is what it was — and the reader can
weigh the finding accordingly.

The clause text is Contract 3's, copied byte-identical into each of the four skills. Phase 3
pins the insertion anchor per file.

---

## How the units depend on each other

The profile's *Dependency rule* orders these; the ordering is not a preference.

| Unit | Issue | Depends on | Why |
|---|---|---|---|
| 1 — Define the grammar | CDR-10 | — | Nothing can emit or cite a grammar that is not written |
| 2 — Setup emits it | CDR-11 | Unit 1 | Emits Contract 1's text and Contract 2's legend |
| 3 — Read the schema version | CDR-12 | Unit 1 (version numbers only) | Needs FR-011's numbers, not the grammar text |
| 4 — Convert existing artifacts | CDR-13 | Units 1, 2 | Converts *to* the grammar, through the emitter's diff-and-propose path |
| 5 — Cite grounding in findings | CDR-14 | Unit 1 | Copies Contract 3 verbatim |
| Integration | *to be created in Phase 2* | 1–5 | See below |

**Unit 3 is the parallel one.** Its only coupling to Unit 1 is three integers, so it can be
built alongside Unit 2 once FR-011's numbers are fixed. Units 4 and 5 both wait on Unit 1;
Unit 4 additionally waits on Unit 2 because it reuses the emitter's proposal path rather than
writing a second one.

**The integration unit does not exist yet.** Phase 1A could not create it — Linear was
unreachable that session. Linear is reachable now, and Phase 2 creates it with the
`integration` label per the Linear conventions.

---

## Testing strategy

The kit's test convention is one executable file run directly with `node`, using `node:assert`
with `fs.mkdtempSync` scratch directories. There is no runner, no watch mode, and no coverage
tool. A new behaviour is proven by adding assertions to
`ai-delivery/tests/portability-conformance.js`.

**Consequence for the profile's *Test-first meaning*:** assertions are still written before the
behaviour, but the artifact is a block appended to the existing file, not a new per-unit test
file. `.ai-delivery/gates.md` thresholds do not transfer — they describe kit-scratch's
pytest-cov setup, and the kit repository has no coverage tool. The bar here is the assertion
list below, in full.

### Executable assertions — Unit 3

| # | Assertion | Proves |
|---|---|---|
| 1 | `schemaVersionDrift` on an empty root returns `[]` | No `.ai-delivery/`, no noise |
| 2 | All three artifacts at current versions → `[]` | The silent case is silent |
| 3 | `conventions.md` at 1 → one entry `{conventions.md, 1, 2}` | The core report |
| 4 | `conventions.md` at 1 and `gates.md` at 1 → two entries | Multiple drift accumulates |
| 5 | `rubrics.md` at 4 → one entry flagged as ahead | Newer-kit artifacts are not called stale |
| 6 | Artifact with no `schema_version` line → `[]` | ADR-004 |
| 7 | Artifact with `schema_version: banana` → `[]` | Malformed degrades to silence, never throws |
| 8 | Unreadable / permission-denied artifact → `[]` | Failure is a return value |
| 9 | CRLF artifact at version 1 → reports drift | Matches existing CRLF fixtures |
| 10 | `config.md` at any version → never an entry | The map's deliberate omission |

### Contract-preservation assertions — the load-bearing ones

| # | Assertion | Proves |
|---|---|---|
| 11 | The nine existing `deepStrictEqual(evaluateGate(...))` cases pass unmodified | `evaluateGate`'s shape is untouched |
| 12 | `runGateClassProof()` passes unmodified, 11 blocking / 2 advisory | No skill's gate stanza changed |
| 13 | Spawned `gate` with drifting artifacts: stdout byte-identical, exit code identical, to the same root without them | **ADR-002's whole claim**, asserted rather than argued |
| 14 | That same spawn's stderr matches `/^ai-delivery setup runtime: advisory: /` and is exactly one line | The advisory is well-formed and bounded |
| 15 | Spawned `gate` with no drift emits empty stderr | No advisory when there is nothing to say |

Assertion 13 is the one that would catch the failure this design most needs to avoid. It
compares two live spawns rather than reasoning about the code, so it stays true if someone
later adds an unrelated write to `main()`.

### Text assertions — Units 1, 2, 4, 5

These are markdown contracts, and the kit already asserts on markdown text elsewhere in the
same file (`assert.match(setupText, /preserve stdout exactly/)`).

| # | Assertion | Proves |
|---|---|---|
| 16 | `artifact-schemas.md` contains no `verified:` in § 1 | FR-001's replacement is complete |
| 17 | § 1 defines all three state tokens and the absence rule | FR-001..FR-004 |
| 18 | § 1's tier table contains all six tiers including `1-kit` | ADR-003 landed |
| 19 | The § 8 clause text and each of the four skills' copies are byte-identical | One definition, four copies, no drift |
| 20 | No `SKILL.md` defines a local variant of the grammar | The requirements' § 8 single-vocabulary rule |
| 21 | The § 4 conventions skeleton has no unannotated bullet | FR-010, the grep criterion, mechanised |
| 22 | `read_on` appears in no function name, exported symbol, file name, or fixture path | The verb is substitutable — FR-015's escape hatch |

Assertion 22 is what makes "provisional" a property rather than a promise. If the FR-015 gate
comes back against `read_on`, this assertion is the evidence that the change is a text
substitution.

### What is not tested, and why

- **No load, performance, or soak testing.** Nothing here runs at request rate. The reader
  performs three file reads inside a command that already reads several.
- **No integration-with-external-service testing.** There are no external services. The single
  existing fetch path gains failure recording and no new capability.
- **No end-to-end browser or UI testing.** `ui_facing: false`.
- **Content drift is not tested because it is not detected.** A source that still resolves but
  no longer supports the claim is out of scope by § 3 and named as a limitation in § 10 of the
  requirements. No assertion here implies otherwise.

### End-to-end proof

Per the profile's *Verification method* and *Integration meaning*, the feature is proven when a
single run shows the whole path:

1. Run setup in a fresh repository. Every kit-written line in all three artifacts carries an
   annotation; no line carries `verified:`; the legend is present in each file.
2. Point a source URL at a host that does not resolve. That line carries `unreachable:` with
   the attempt date, no `read_on:`, and the operator is told at run time which sources failed —
   with no fetched content quoted back into the message.
3. Run the gate against artifacts written under the old grammar. stdout is one status word,
   the exit code is unchanged, and the advisory appears on stderr.
4. Re-run setup against those old artifacts. The conversion is *proposed*; `3-model` lines lose
   their dates; grounded lines keep theirs; nothing is applied without confirmation.
5. Run critique against a repository with an `ungrounded` threshold. A finding that cites it
   says so rather than calling it verified.

Step 2 carries a security constraint from the requirements' § 7 that is easy to lose in
implementation: the operator message must not embed content derived from a fetch response,
because artifact text is read as authoritative by every later agent run.

---

## Backward compatibility

| Surface | Guarantee |
|---|---|
| Gate stdout vocabulary | Unchanged — `MISSING`, `STALE`, `FRESH`, one word, one line |
| Gate exit codes | Unchanged — 2 blocking on MISSING/STALE, 0 otherwise |
| `evaluateGate()` return shape | Unchanged — `{ status, exitCode }`, no added key |
| The thirteen skills' gate stanzas | Unchanged — not one file edited |
| `path-guard.js`, the hooks, CI | Untouched, by requirement |
| Old-grammar artifacts | Remain readable. They do not remain *valid*, and they declare which grammar produced them |
| Hand-edited artifacts | Survive. Nothing parses annotations; a human-rewritten line is a human-authored line |
| `module.exports` | Additive only — the test imports by destructuring |

An artifact written under the old grammar is never silently misread: its `schema_version`
declares its grammar, and the reader says so. That is the whole of the backward-readability
requirement, and it is the reason Unit 3 exists at all.

---

## Open items

**FR-015 has not run, and the verb is provisional.** Every occurrence of `read_on` in this
document is a placeholder for the chosen event verb. The maintainer decided on 2026-08-27 to
carry it provisionally through the specifications and run the gate before implementation
begins in the kit repository. Assertion 22 keeps the substitution cheap. **Owner: the kit
maintainer.**

**Nothing else in this document is unsettled.** ADR-003 is decided, ADR-004 is decided, and
every contract above is stated at the precision Phase 3 needs.

---

## Actions this document surfaces

- **Run the FR-015 validation gate before implementation begins.** Two versions of one
  conventions file, one using `verified:` and one using the candidate verb, put to a model
  asked to classify each line's grounding; record the result. The kit maintainer owns this.
- **Edit the requirements' "Reading the tier codes" preamble to include `1-kit`.** ADR-003
  added vocabulary the requirements' § 8 declared unnecessary, and the requirements document
  now understates the tier list. The kit maintainer owns this.
- **Run `/ai-delivery:setup` in `/Users/maxdamsky/Projects/ai-delivery-kit`.** No conventions,
  gates, or rubrics describe the repository this feature actually changes, so no implementation
  can be verified there. The developer responsible for that repository owns this.

---

## Next Steps

- **Phase 1C — operations.** The plugin version bump as a release gate (a content-only commit
  reports "already at the latest version"), the FR-009 operator message wording under its
  no-embedded-content constraint, the six-month audit date, and the rollback story for a
  conversion someone accepted and regretted.
- **Phase 2 — decomposition.** Confirm the five units against these contracts and create the
  integration unit in Linear, which is reachable this session.
