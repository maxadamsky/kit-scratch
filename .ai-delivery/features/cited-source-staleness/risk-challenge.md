# Risk Challenge: cited-source-staleness — grammar-only honesty fix, enforcement deferred

**Created:** 2026-08-12
**Source:** single-perspective risk pass (one fresh-context subagent)
**Direction assessed:** Candidate A now, B or C later — fix the artifact's honesty in the
annotation grammar alone; defer any mechanical classifier or snapshotting to a later
decision made on evidence.

> One careful pass, one perspective — issues surfaced here are real signals, but this
> is not complete coverage.

Seven risks returned; none merged on de-duplication, as each names a distinct failure.
Cross-referenced against the risk cross-reference seats from Phase 1 (stress `STR-n`,
operator `OPR-n`). Three were independently re-found from a different context, which is the
strongest attention signal this pipeline produces. Four are new — and two of those land on
decisions made during direction setting.

---

## Critical Risks (High Likelihood × High Impact)

### The deferral's evidence can never be collected
- **Category:** Assumption
- **Description:** The direction's whole rationale is that grammar-only is the cheapest way
  to learn whether a reader acts on "last read fourteen months ago." But the constraints
  forbid central state, there is no registry and no telemetry, and the files live in other
  people's repositories. The success metric — a non-zero count of demoted-or-deleted lines
  after a year — requires observing line-level deltas across installs that cannot be seen.
  The MVP ships an experiment with no instrument, and the follow-on decision arrives a year
  later on the same zero evidence, with the grammar already committed into strangers' git
  history.
- **Likelihood:** High
- **Impact:** High
- **Mitigation signal:** Name, before shipping, the specific observation that triggers the
  follow-on decision and where it comes from — a hand-audit of dogfood repos at a fixed
  date, or a question asked during a setup re-run. If no such observation exists, drop the
  evidence framing and admit this is a permanent design choice rather than a probe.
- **Found by:** risk-pass; **independently re-found:** OPR-3 (no install registry, no way to
  ask an install which kit version produced its annotations)

### The absence-means-human invariant is unenforced, and content edits break it silently
- **Category:** Technical
- **Description:** The fourth pile rests entirely on a by-construction claim that the kit
  never writes a bare line, and it breaks three ways. **(a) Legacy inversion** — artifacts
  already in the wild carry bare skeleton bullets, so on those files bare means kit-written,
  the exact opposite of the new rule. **(b) Future emitters** — any new code path that
  forgets an annotation silently manufactures a fake human-authored line, and nothing
  detects it because the check is deferred. **(c) Text drift, the worst one** — hand editing
  is *invited*, so a human who rewrites the text of a kit-written line while leaving the
  annotation intact produces a line whose annotation vouches for wording the cited source
  never contained. That is the original failure re-created inside the new grammar, and it is
  arguably worse, because the reader has now been told the metadata is trustworthy.
- **Likelihood:** High
- **Impact:** High
- **Mitigation signal:** Decide explicitly what an annotation vouches for — the source
  existing at that date, or this exact sentence being supported by it — and state it in the
  grammar. Accept that the fourth pile is heuristic rather than construction, and word the
  file's own legend to claim only what the mechanism delivers.
- **Found by:** risk-pass; **independently re-found (partially):** STR-6 (two grammars in one
  file; the parser reads minority-grammar lines confidently and wrongly) covers (a). Sub-point
  (c) is new — no council member found it.

---

## Significant Risks

*(Medium likelihood or impact — worth addressing before requirements)*

### The verb change is an unvalidated linguistic bet, and the primary reader is a model
- **Category:** Assumption
- **Description:** The direction declares the verb change to be "the substance," while the
  framing declares the agent the worse-affected reader. There is no evidence that a model
  reading an event-word date behaves differently from one reading a state-word date; a bare
  date beside a source URL may read as endorsement regardless of the verb. If agents flatten
  the distinction, the change is honest bookkeeping with zero behavioural effect on exactly
  the party the framing identifies as most at risk — and the accepted cost (a weaker
  agent-side prompt) is paid for nothing.
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation signal:** Test it cheaply before committing the grammar — show a model two
  versions of the same conventions file and ask it to sort lines into the four piles. If it
  cannot distinguish them, the fix is in the surrounding wording, not the field name.
- **Found by:** risk-pass (new — no council member examined reader interpretation)

### Migration of existing artifacts has no path that does not violate a stated must-not
- **Category:** Technical
- **Description:** Files already exist carrying the old field at the old schema version. The
  success criterion "zero occurrences in generated output" is satisfied by newly generated
  files while every existing install keeps the dishonest field forever. Rewriting the field
  in place instead is mechanically converting an unbacked state-claim into a dated
  event-claim about a read that may never have happened — close to the forbidden silent
  re-dating. And if setup regeneration is the migration path, it collides with hand editing
  being invited: regeneration either clobbers team decisions or must merge, and no merge
  strategy is specified. This is where the direction's own rules deadlock.
- **Likelihood:** High
- **Impact:** Medium
- **Mitigation signal:** Write the old-file behaviour into this MVP rather than deferring it.
  Leaving old files legibly old — annotated as predating the guarantee rather than migrated
  at all — is probably the honest answer, and it needs to be a decision rather than an
  omission.
- **Found by:** risk-pass; **independently re-found:** STR-5 (dates laundered through
  merges), STR-6 (two grammars in one file)

### The empty run-record slot violates the direction's own standing constraint
- **Category:** Scope
- **Description:** Scope item 6 defines a grammar slot for a dated run record that nothing in
  this MVP fills, while the standing constraint adopted in the same session says no new field
  ships that setup cannot fill from something real — and the exclusions ban a reserved field
  for a future snapshot reference. The run-record slot is a reserved field under a different
  name. It also reproduces the defect being corrected: `schema_version` was written by
  everything and read by nothing, and is cited in this very direction as the mistake.
  Shipping an always-empty run record teaches the same lesson — that parts of this file are
  decorative — inside the change meant to stop teaching it. An empty record also reads as
  "no problems found" to a reader who does not know it is unfillable.
- **Likelihood:** Medium
- **Impact:** Medium
- **Mitigation signal:** Cut item 6 from the emitted artifact. If the record's shape is
  genuinely needed to constrain later work, put it in the design record rather than the
  file. A viable reconciliation: define the *rule* that a pass writes a record when it runs,
  and that absence of a record means no pass has ever run — which delivers the
  ran-and-fine versus never-ran distinction that motivated item 6, while shipping nothing
  empty.
- **Found by:** risk-pass (new — this contradiction was created during direction setting and
  no council member saw the direction)

### "No code" is inaccurate, and the contract clause fans out into every skill
- **Category:** Scope
- **Description:** The direction is sold as no code, no network, no new enforcement, but the
  MVP requires changing setup's writer, threshold emission, skeleton emission, a non-200
  check in the fetch path, a reader for `schema_version`, and — item 7 — a clause added to
  the contract every skill copies. That last is the highest fan-out edit in the kit. The
  perceived cheapness is what justified choosing this direction over the alternatives, so if
  the real price is "touch every skill plus the setup writer plus a schema reader," the
  comparison that produced the choice was made on a wrong number.
- **Likelihood:** Medium
- **Impact:** Medium
- **Mitigation signal:** Count the files the contract clause actually lands in before
  committing, and re-check whether the direction still wins at that price. If the clause is
  the expensive half and the field rename the cheap half, consider whether they must ship
  together.
- **Found by:** risk-pass (new)

### Suppressing annotations on non-200 turns transient failures into permanent ungrounded lines
- **Category:** Technical
- **Description:** Scope item 5 makes setup emit no source annotation when a fetch returns
  non-200. A 429, a 503, a corporate proxy interstitial, or a captive portal during one setup
  run then produces lines that read as ungrounded forever, with no record distinguishing "no
  source exists" from "the fetch failed at 14:02 that Tuesday." A documentation host that
  rate-limits after the first few fetches degrades a whole conventions file at once, and the
  person running setup never learns it happened.
- **Likelihood:** Medium
- **Impact:** Medium
- **Mitigation signal:** Decide whether setup surfaces fetch failures to the operator at run
  time, and whether a failed fetch is distinguishable in the file from one never attempted.
  At minimum retry once and tell the human what did not resolve while they are still there.
- **Found by:** risk-pass; **independently re-found:** STR-1 (throttled fetches read as dead
  sources) — the same mechanism, inverted: STR-1 found it causing wrongful *expiry* at
  verification time, the risk pass found it causing wrongful *ungrounding* at authoring time

---

## Watch Items (Lower priority, worth tracking)

None. Every risk returned scored Medium or High on both axes; nothing landed low enough to
file here. Recorded explicitly rather than omitted, so a later reader does not read the empty
section as an oversight.

---

## Unstated Assumptions

| Assumption | Consequence if Wrong |
|---|---|
| A reader — especially an agent — interprets an event-word date differently from a state-word date | The verb change is declared to be the substance of the MVP. If both readings collapse to "someone checked this," the change is a rename, the accepted cost of a weaker agent-side prompt is paid, and none of the benefit arrives. |
| An annotation stays truthful as long as its source is unchanged — the rule text beside it does not drift | Hand editing is invited. A human rewriting a kit line while leaving the annotation attached creates a line citing a source for a claim it never made. The original problem under a new field name, with nothing in this direction able to notice. |
| Deferring the classifier is cheap and reversible | Grammar ships into other people's committed git history. Every install adopting v2 raises the cost of v3 — a second migration, a second bump, a second set of legacy files. Deferral usually reduces cost; here it may increase the cost of the deferred thing, inverting the argument for deferring. |
| The single observed 404 is representative of how sources fail | If the dominant real failure is "URL resolves and the content changed" rather than "URL 404s," then even the deferred classifier addresses the minority case, and this grammar is optimised around the wrong failure mode. |

---

## Top Concern

The direction produces information and defers every mechanism that produces action, then
justifies the deferral with evidence it has no way to collect. The framing is explicit that
the expected outcome is demotion, and that a mechanism where nothing is ever dropped is
theatre. This MVP contains nothing that prompts anyone to demote anything — no flagged list,
no filled run record, no moment where a reader is confronted with a line. It replaces a
standing claim with a dated fact and hopes a human notices the date. Meanwhile the constraint
set makes it structurally impossible to learn whether anyone did, so the later decision has
no trigger, no data source, and no owner — the standard shape of a deferral that never
resolves. A year on, the honest position is "we changed a word, we do not know if it helped,
and the grammar is now committed in N repos so changing it again is more expensive than it
was today."
