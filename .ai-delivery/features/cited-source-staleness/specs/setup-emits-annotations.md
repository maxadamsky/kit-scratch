# Code Spec: Write honest annotations when setup generates artifacts

**Unit:** CDR-11 — Write honest annotations when setup generates artifacts
**Design Reference:** `design/1b-contracts.md` Contracts 1 and 2; `design/1c-operations.md` § Security design
**Date:** 2026-08-27
**Target repository:** `/Users/maxdamsky/Projects/ai-delivery-kit`

## Implementation Summary

- **Files to Create:** 0
- **Files to Modify:** 2
- **Assertions to Add:** ~8 emitter-behaviour assertions
- **Estimated Complexity:** L

This unit changes instructions an agent follows, not code a runtime executes. Its correctness
is therefore proven the way the kit already proves instruction correctness — by asserting on
the text of `SKILL.md`, and by the end-to-end run in the integration unit.

## Codebase Conventions

**Instruction style in `SKILL.md`:** numbered phases as H2 (`## Phase 6 — Generate`), each
phase a short imperative list. Rules are stated as obligations, not suggestions. Tables carry
check-and-consequence pairs. Do not add a new phase; extend the two that exist.
**Artifact generation is specified by reference:** Phase 6 says "Write the artifacts exactly
per `references/artifact-schemas.md`". That indirection is the pattern — this unit changes
*what setup does at generation time*, while CDR-10 changes *what the artifacts must contain*.
Keep the split; do not restate the grammar in `SKILL.md`.
**Verification Framework:** `node:assert` in `ai-delivery/tests/portability-conformance.js`.
**Self-check discipline:** Phase 6 already ends with a self-check list that greps the written
artifacts and requires a FRESH gate. New emitter obligations get new self-check entries there
rather than a new mechanism.

## Technical Context

**Key Gotchas**

- **The grammar lives in one place.** `SKILL.md` must not restate the state tokens or tier
  definitions. It says *emit per the schema*; CDR-10 owns what that means. Restating it
  creates a second definition that will drift.
- **The Linear Conventions section is generated from the § 4 skeleton**, so CDR-10's
  re-annotation of that skeleton is what actually fixes the eight bare bullets in a generated
  `conventions.md`. This unit's obligation is that generation carries the annotations through
  rather than dropping them — and that any team-taxonomy line setup *adds* on top of the
  skeleton is annotated too.
- **The Core Rubric carries no per-item annotation** and its byte-exact diff is already a
  self-check step. FR-010's "every line annotated" must not be read as overriding that
  exception, or the self-check starts failing on correct output.
- **Scale of the change.** A generated repository carries roughly 65 annotations — measured
  2026-08-27: 41 in `conventions.md`, 22 in `rubrics.md`, 2 in `gates.md`. Every one moves to
  the new grammar, and the thresholds block gains annotations it does not have today.

**Reusable Utilities:** the existing Phase 6 self-check grep list; the existing Phase 3 tier
ladder.

**Integration Points:** consumes CDR-10's grammar and skeletons. Publishes the three
`schema_version` values CDR-12 reads. CDR-13 extends the same diff-and-propose path.

## Contracts

### Generation behaviour (Phase 6)

| Behaviour | Obligation | Failure signal |
|---|---|---|
| Emit a read | Every line grounded in a source read during this run carries `read_on:` with **this run's** date | A carried-forward date on a line not re-read |
| Emit a failure | Every line whose source was fetched and did not resolve carries `unreachable:` with the attempt date and **no** source annotation claiming a read | A `read_on:` on a line whose fetch failed |
| Emit an absence | Every `3-model` line and every scaffold-default threshold carries bare `ungrounded` | A date on a `3-model` line — the original defect |
| Cover every line | Every kit-written line contains `[source:` | A bare bullet, making a kit line look human-written |
| Write the legend | Each of the three artifacts carries the legend in `## About This File` | A legend in one file but not another |
| Write the version | `conventions.md` 2, `gates.md` 2, `rubrics.md` 3 | Any other value; CDR-12 then reports drift on a freshly generated file |

**The thresholds block is the sharpest case.** Today `gates.md` emits
`coverage_branch: 70 [source: scaffold default, confirmed · tier: 1-docs · verified: <date>]`
and leaves the other five thresholds unannotated. After this unit every scaffold default
carries `[source: none · tier: 3-model · ungrounded]`, and only a threshold actually read from
project config carries `read_on:`.

### Fetch-failure behaviour (Phase 3)

**Component:** the research phase's tier ladder, step 1 (official documentation, fetched).

| Behaviour | Obligation |
|---|---|
| Retry | One retry before recording a failure. Not a loop — a retry loop inside a setup run makes a network partition look like a hang |
| Record | After the retry fails, the line carries `unreachable:` with the attempt date. It never silently falls through to `3-model` with a date |
| Report | The operator is told at run time which sources did not resolve |

**Failure conditions, named once each:** *fetch failed* covers both a non-200 response and a
transport failure; the two are distinguished in the operator message but produce the same
annotation state, because the artifact's reader cares only that a fetch was attempted and did
not resolve.

### The operator message — a security contract, not a formatting choice

The message **must not embed content derived from a fetch response.** Specifically:

- **Report** the requested URL, exactly as it appeared in `references/source-catalog.md` or in
  the user's input, and the failure class — a transport failure, or an HTTP status as an
  integer.
- **Never report** the response body, any response header, an error page's text, a page
  title, or **the final URL after redirects**.

The redirect clause is the one an implementer would most plausibly skip, and it is the one
that matters most. A redirect target is chosen by the remote host, so echoing the resolved URL
hands a hostile or compromised host a short string in the operator's terminal — and from
there, plausibly, into an artifact. The requested URL came from the kit or the user and is
safe to repeat; the resolved one did not.

The reason this is a hard rule rather than caution: **artifact text is read as authoritative by
every later agent run.** That is the trust boundary this feature has, and it is not a network
boundary.

`design/1c-operations.md` § Security design carries the message's shape.

### The legend

Contract 2 in `design/1b-contracts.md` carries the exact prose. Emitted verbatim into
`## About This File` in all three artifacts. It must state three things, and each is checked:
the annotation's promise as a **conjunction** (someone read this source on this date *and the
line follows from it*), the editor's obligation in the second person, and the admission that
the human-authored distinction is heuristic.

The legend is the only part of the mechanism a reader meets without being told to look for it,
which is why it is specified as exact text rather than as intent.

## Pre-Implementation Assertions

**Pattern file:** `ai-delivery/tests/portability-conformance.js:427` —
`assert.match(setupText, /preserve stdout exactly[\s\S]*as \`hook_runtime\`/)`. That is the
kit's existing way of asserting that `SKILL.md` carries a required instruction. Imitate the
read-then-match shape.

**Cases**
- `SKILL.md` Phase 6 requires `read_on:` for a source read during the run
- Phase 6 requires bare `ungrounded` for `3-model` lines and scaffold defaults, and states
  that no date is written on them
- Phase 6 requires the legend in all three artifacts
- Phase 6 states the three `schema_version` values
- Phase 6's self-check list includes a grep for `verified:` returning zero, and a check that
  no kit-written line lacks `[source:`
- Phase 3 requires one retry before recording `unreachable:`
- Phase 3 forbids embedding fetch-response content in the operator message, **and names the
  post-redirect URL among the forbidden items**
- `SKILL.md` does not restate the grammar's tier definitions or state tokens — the single
  definition stays in `artifact-schemas.md`

**Integration scenarios** — exercised by the integration unit, listed here so this unit knows
what it must make possible:

| Scenario | Steps | Expected outcome |
|---|---|---|
| Clean run | Run setup in a fresh repository | No `verified:` in any artifact; every kit-written line matches `[source:`; legend present ×3 |
| Dead source | Point a catalog URL at a non-resolving host, run setup | That line carries `unreachable:` with today's date; operator message names the requested URL and failure class only |
| Scaffold thresholds | Run setup where the project configures no coverage threshold | Every scaffold threshold carries `ungrounded`, none carries a date |
| Version stamps | Read the three artifacts' frontmatter | 2, 2, 3 |

## Task Breakdown

### Task 1: Add the assertions (test-first)

**Dependencies:** None (CDR-10's text must exist for the grammar-single-definition assertion
to be meaningful, but the assertions themselves are written first)
**Files:** `ai-delivery/tests/portability-conformance.js` (modify)
**Pattern:** line 427

### Task 2: Phase 6 — generation obligations

**Dependencies:** Task 1
**Files:** `ai-delivery/skills/setup/SKILL.md` (modify)

Edit the numbered artifact list in `## Phase 6 — Generate`:

- Item 2 (`gates.md`): "thresholds with provenance" becomes explicit about state — a threshold
  read from project config carries `read_on:`; every scaffold default carries `ungrounded`
  with no date.
- Item 3 (`conventions.md`): replace the literal `[source · tier · verified]` with a pointer to
  the schema's grammar, and add the obligation that team-taxonomy lines setup adds on top of
  the § 4 skeleton are annotated like any other kit-written line.
- Item 4 (`rubrics.md`): update the parenthetical from "schema 2" to schema 3, keeping the
  `generated_under_profile` explanation intact — that sentence is load-bearing for the § 8
  provenance check.
- All three: state that the legend from the schema is written into `## About This File`.

### Task 3: Phase 6 — self-check additions

**Dependencies:** Task 2
**Files:** `ai-delivery/skills/setup/SKILL.md` (modify)

Add to the existing self-check list, in its established style:

- Grep each artifact for `verified:` — any occurrence is a failure to fix.
- Confirm no kit-written line lacks `[source:`, **excluding Core Rubric items**, whose
  byte-exact diff is already the adjacent check.
- Confirm each artifact's `schema_version` is the value the schema states.

Follow the existing instruction that these use Read/Grep operations, not a shell command —
that is a portability rule, and it is tested.

### Task 4: Phase 3 — fetch failure recording

**Dependencies:** Task 1
**Files:** `ai-delivery/skills/setup/SKILL.md` (modify)

Extend step 1 of the tier ladder: on a failed fetch, retry once; if it fails again, the line
carries `unreachable:` with the attempt date rather than falling through to `3-model`.

State the distinction explicitly, because it is the one a reader of the artifact depends on:
a failed fetch is **not** the same as no source ever existing, and the ladder must not collapse
the two.

### Task 5: Phase 3 — the operator message

**Dependencies:** Task 4
**Files:** `ai-delivery/skills/setup/SKILL.md` (modify)

Add the reporting obligation and its prohibition. Write the prohibition as an explicit list of
what may not appear — body, headers, page text, title, post-redirect URL — rather than as a
general caution. A general caution is what an implementer optimises away.

Give the reason in one sentence in the file itself: artifact text is read as authoritative by
every later agent run. A rule whose reason is absent gets relaxed by the next person to touch
it.

## Task Dependency Graph

```
Task 1 (assertions, test-first)
   ├─→ Task 2 (Phase 6 obligations) ──→ Task 3 (Phase 6 self-check)
   └─→ Task 4 (Phase 3 retry+record) ──→ Task 5 (Phase 3 operator message)
```

Tasks 2–3 and 4–5 are independent chains within this unit.

## Pattern References

**Instruction pattern:** `ai-delivery/skills/setup/SKILL.md` `## Phase 6 — Generate` — imitate
its numbered-artifact structure and its self-check-at-the-end discipline. New obligations go
inside the existing shape.

**Assertion pattern:** `ai-delivery/tests/portability-conformance.js:427` — read the skill
text, match the required instruction.

## Implementation Notes

**Security.** The operator-message prohibition above is this unit's whole security surface and
it is not optional. No new outbound path is introduced: the research phase gains failure
*recording*, not a new capability or a new source.

**Performance.** One retry per failed fetch. No retry loop, no backoff schedule, no parallel
fetching — a setup run is interactive and a partition must not look like a hang.

**Deployment.** Content-only change; the plugin version bump is the integration unit's.

**Post-implementation verification.** Run setup in a scratch repository and grep the three
generated artifacts. Zero `verified:`; every kit-written line outside the Core Rubric matches
`[source:`; three legends present; versions 2, 2, 3.

## Final Verification

**Functionality**
- [ ] All nine acceptance criteria in the skeleton met
- [ ] A failed fetch produces `unreachable:` and never a `read_on:`
- [ ] Scaffold thresholds carry `ungrounded` with no date

**Quality**
- [ ] `SKILL.md` does not restate the grammar — one definition, in `artifact-schemas.md`
- [ ] The Core Rubric exception is preserved and its byte-exact diff still passes
- [ ] The operator-message prohibition names the post-redirect URL explicitly

**Testing**
- [ ] Emitter assertions added and passing
- [ ] Full conformance suite passes with pre-existing cases unmodified

**Open before merge**
- [ ] **FR-015 has run.** `read_on` is provisional; the verb this unit emits is not final until
      the gate runs. Owner: kit maintainer.
