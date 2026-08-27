# Code Spec: Integrate and prove the annotation grammar end to end

**Unit:** the integration unit — **not yet created in Linear** (see below)
**Design Reference:** `design/1b-contracts.md` § Testing strategy; `design/1c-operations.md` § Release and distribution
**Date:** 2026-08-27
**Target repository:** `/Users/maxdamsky/Projects/ai-delivery-kit`

## Why this issue does not exist yet

Decomposition was approved on 2026-08-27 with the Linear write declined: the skeletons and
specs were written to the repository and the tracker was left untouched.

Creating the issue is a pending action with the kit maintainer as owner. It must be a
**top-level** issue in the project (never a sub-issue — it spans all units), carrying the
`integration` label, assigned to the final milestone "Existing projects and agent findings",
and blocked-by CDR-10, CDR-11, CDR-12, CDR-13, and CDR-14. Record its identifier in
`tracker.md § Build` immediately after it is created.

Nothing downstream is blocked by the absence — the five component units are tracked, and this
spec is the record of what integration consists of.

## Implementation Summary

- **Files to Create:** 0
- **Files to Modify:** 2 (`portability-conformance.js`, `plugin.json`)
- **Assertions to Add:** the five end-to-end scenarios, plus reconciliation of the five units' blocks
- **Estimated Complexity:** M — measured, per the profile, in shared-file count: two

## Shared File Analysis

**Resolved by restructuring:**

- `ai-delivery/skills/setup/references/artifact-schemas.md` — CDR-10 and CDR-11 both had a
  claim on it: the requirements put the § 3/§ 4/§ 5 skeletons under "grammar definition" but
  put FR-010 ("every line setup writes carries an annotation") under the emitter. Given
  entirely to CDR-10 — the skeleton text is grammar; the behaviour that emits against it is
  CDR-11's `SKILL.md` change. **Conflict eliminated, not deferred.**

**Accepted conflicts — Phase 4 batches these sequentially:**

- `ai-delivery/tests/portability-conformance.js` — **all five units append assertions to it.**
  The kit has exactly one test file, run directly with `node`, with no runner and no discovery
  mechanism. Splitting it would invent a new test convention in a repository whose portability
  is a hard, tested constraint; moving all assertions here would break the profile's test-first
  rule. Accepted on the maintainer's decision of 2026-08-27, as the guide's `requirements.txt`
  case.
- `ai-delivery/skills/setup/SKILL.md` — CDR-11 and CDR-13. Genuine: CDR-13 reuses CDR-11's
  diff-and-propose path rather than writing a second one. Expressed as an ordering edge.

**Result, stated plainly rather than dressed up:** there is **no parallel first batch.** The
shared test file conflicts with every pair, so the five units serialize:

```
Batch 1 → CDR-10  Define the grammar          (Urgent; everything depends on it)
Batch 2 → CDR-11  Setup emits it              (Urgent; must precede CDR-13)
Batch 3 → CDR-12  Read the schema version     (High; needs only FR-011's three numbers)
Batch 4 → CDR-13  Convert existing artifacts  (Medium; after CDR-11 — shared SKILL.md)
Batch 5 → CDR-14  Cite grounding in findings  (Medium)
Batch 6 → this integration unit
```

The cost is low here and the reason is worth recording: every unit is a small text edit to a
specification file, so serialization spends ordering, not weeks. A feature with heavier units
and this same test-file constraint would deserve the other answer.

## Technical Context

**Key Gotchas**

- **Five assertion blocks were written independently.** Reconciling them is real work: duplicate
  fixture helpers, colliding scratch-directory names, and case numbering that no longer runs in
  sequence. The suite must pass as a whole, not as five passing fragments.
- **The pre-existing cases must still be unmodified.** If any unit edited the nine
  `deepStrictEqual(evaluateGate(...))` cases or `runGateClassProof()`, that unit broke its
  boundary and the edit is the defect — not the assertion.
- **No mocks to replace.** The decomposition used no mock or interface isolation, because no
  unit calls another — the coupling here is shared text, not runtime dependency. This is
  recorded rather than glossed: the profile recommends the mock/interface pattern for
  parallelism, and this feature had nothing to apply it to.

**Integration Points:** every file the five units touch.

## What "wired together" means here

The profile's *Integration meaning* translated for a repository whose product is
specification text:

| Profile's term | This feature's form |
|---|---|
| Shared file merges | The five assertion blocks reconciled into one file that runs clean as a whole |
| Mocks replaced by real implementations | **None** — no unit called another |
| Import verification | Cross-file consistency: the § 8 clause and its four copies byte-identical; the grammar defined in exactly one place; every tier list carrying all six tiers |
| End-to-end tests | The five scenarios below, run against a real setup invocation |

## End-to-End Scenarios

| Scenario | Steps | Expected outcome |
|---|---|---|
| Clean generation | Run setup in a fresh repository | Every kit-written line outside the Core Rubric matches `[source:`; zero `verified:`; the legend present in all three artifacts; versions 2, 2, 3 |
| Dead source | Point a catalog URL at a non-resolving host; run setup | That line carries `unreachable:` with the attempt date and no `read_on:`; the operator message names the requested URL and failure class and contains nothing from the response — **including no post-redirect URL** |
| Old artifacts at the gate | Run a gated skill against artifacts at `schema_version: 1` | stdout is one status word, exit code unchanged, one advisory line on stderr |
| Conversion | Re-run setup against those artifacts | Conversion proposed, not applied; `3-model` lines lose their dates; grounded lines keep theirs; no date moves forward |
| Honest finding | Run critique against a repository with an `ungrounded` threshold, on code below it | The finding says the threshold has no source rather than calling it a verified standard |

## Task Breakdown

### Task 1: Confirm every component unit is verified

**Dependencies:** CDR-10, CDR-11, CDR-12, CDR-13, CDR-14
**Files:** none

Integration does not begin while any unit is unverified or escalated.

### Task 2: Reconcile the assertion blocks

**Dependencies:** Task 1
**Files:** `ai-delivery/tests/portability-conformance.js` (modify)

Merge the five blocks into a coherent file: one set of fixture helpers, no scratch-directory
collisions, case numbering sequential, and the stage summary lines reporting true counts. The
file's existing stage structure is the organising principle — do not add a sixth stage for this
feature; distribute assertions into the stages they belong to.

### Task 3: Add the end-to-end assertions

**Dependencies:** Task 2
**Files:** `ai-delivery/tests/portability-conformance.js` (modify)

The five scenarios above. The gate-related ones use the existing spawn helpers
(`runGateCommand`, `gateCommand`); the setup-run ones are necessarily manual, and where a
scenario cannot be automated the spec says so rather than asserting a weaker proxy.

**Explicitly:** the "clean generation" and "dead source" scenarios require running setup, which
is an agent workflow rather than a callable function. Record them as a **manual release
checklist** in this unit's closing report, and do not fake them with an assertion that only
checks the instruction text — CDR-11 already asserts the instruction text, and re-asserting it
here would be proof of nothing.

### Task 4: Verify cross-file consistency

**Dependencies:** Task 2
**Files:** `ai-delivery/tests/portability-conformance.js` (modify)

- The § 8 clause and its four copies byte-identical
- The grammar's state tokens defined in exactly one file
- Every tier list in the repository names all six tiers
- No skill defines a local variant

Most of these are CDR-10's and CDR-14's assertions; this task confirms they still hold **after
all five units have landed**, which is the only point at which cross-unit drift can appear.

### Task 5: Bump the plugin version

**Dependencies:** Tasks 2–4 passing
**Files:** `ai-delivery/.claude-plugin/plugin.json` (modify)

Bump `version` from `1.9.0`. **1.10.0 is the recommendation:** the gate's stdout vocabulary,
exit codes, and `evaluateGate()`'s return shape are unchanged, no skill's gate stanza is
edited, and old artifacts remain readable. What changes is the generated output format, and
that break is already signalled where it belongs — in each artifact's own `schema_version`.
The kit maintainer owns the final call.

### Task 6: Verify the bump by installing

**Dependencies:** Task 5
**Files:** none

Install from the marketplace into a scratch repository and confirm the new version is what
arrives.

**This is not ceremony.** Task 5 changes a number in a file; Task 6 is the only thing that
proves the number had the intended effect. The failure being guarded against is precisely
"believed to have shipped, did not" — a content-only commit reports *already at the latest
version* — which is this feature's own subject one level up.

### Task 7: Record the audit date

**Dependencies:** Task 6
**Files:** the release record

Six months from the ship date is the proposed default; requirements Q2 owns the interval and
targets the decision at release. Whatever interval is chosen, **the date is written down.** An
audit with no recorded date does not happen, and it is the only instrument answering whether
the deferred classifier is needed.

## Task Dependency Graph

```
Task 1 (all units verified)
   └─→ Task 2 (reconcile blocks) ─┬─→ Task 3 (e2e assertions) ─┐
                                   └─→ Task 4 (cross-file)  ────┤
                                                                └─→ Task 5 (version bump)
                                                                      └─→ Task 6 (verify install)
                                                                            └─→ Task 7 (audit date)
```

## Pattern References

**Suite structure:** `ai-delivery/tests/portability-conformance.js` — its existing stage
functions and their `PASS stage<N> …` summary lines. Distribute into them; do not append a
parallel structure.

**Spawn-based gate proof:** `runGateClassProof()` (lines 218–246) — the pattern for any
assertion that must exercise a real command rather than a function.

## Implementation Notes

**Security.** Nothing new. The one security contract in the feature — CDR-11's operator-message
prohibition — is verified here by the dead-source scenario, manually.

**Performance.** Confirm CDR-12's limits still hold after reconciliation: three file reads,
three regex executions, no directory walk, no second read of any file.

**Deployment.** Tasks 5–7 are the release gate. All three are the kit maintainer's.

## Final Verification

**Functionality**
- [ ] All eight acceptance criteria in the skeleton met
- [ ] All five end-to-end scenarios pass, the two manual ones executed and recorded

**Quality**
- [ ] Suite passes as a whole, with the nine `deepStrictEqual` cases and `runGateClassProof()`
      unmodified
- [ ] All five copies of the § 8 clause byte-identical
- [ ] The grammar defined in exactly one place

**Release**
- [ ] `plugin.json` version bumped
- [ ] The bump verified by installing from the marketplace into a scratch repository
- [ ] The audit date recorded

**Out of scope — and the closing report must not imply otherwise**
- The mechanical annotation classifier. Deferred pending the audit's evidence.
- Content drift — a source that still resolves but no longer supports the claim. Nothing in
  this feature addresses it; it is R10 and the requirements' most important caveat.
- The backfill gap (R2): a repository whose stack never changes is never offered the
  conversion.

## The two gates that are not code

Both are the kit maintainer's, and both must be closed before this unit can complete:

1. **FR-015 has not run.** The `read_on` verb is provisional through every document and spec in
   this feature. The grammar is not merged until a model has been shown both versions and its
   ability to distinguish them is recorded.
2. **The version bump must be verified by installing, not by editing.**
