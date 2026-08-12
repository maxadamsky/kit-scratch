## Risk Challenge Output

### Risks

**Risk 1: The deferral's evidence can never be collected**
- **Category:** Assumption
- **Description:** The whole rationale is "grammar-only is the cheapest way to get data on whether a reader told 'last read fourteen months ago' ever acts on it." But the constraints forbid central state, there is no registry, no telemetry, and the files live in other people's repositories. The framing's own measurable signal — "after the first year, the count of demoted-or-deleted lines is non-zero" — requires observing line-level deltas across installs you cannot see. So the MVP ships an experiment with no instrument. The follow-on decision will be made on the same zero evidence it is being deferred to avoid, except a year later and with a grammar already committed into strangers' git history.
- **Likelihood:** High
- **Impact if realized:** High
- **Mitigation signal:** Name, before shipping, the specific observation that would trigger the follow-on decision and where it comes from (own dogfood repos with a hand-audit at a fixed date? a question in setup re-run?). If no such observation exists, drop the evidence framing and admit this is a permanent design choice, not a probe.

**Risk 2: The verb change is an unvalidated linguistic bet, and the primary affected reader is a model**
- **Category:** Assumption
- **Description:** "The verb change is the substance." The framing says the agent is the worse-affected party — it treats `verified:` as a fact and never clicks the link. There is no reason to expect an LLM reading `read_on: 2024-03-12` to behave differently from one reading `verified: 2024-03-12`; models routinely normalize near-synonymous metadata into "this was checked, it's fine," and a bare date next to a source URL reads as an endorsement regardless of the verb. The entire mechanism's efficacy rests on a subtle event-vs-state distinction that has not been tested against either an agent or a human reader. If agents flatten it, the change is honest bookkeeping with zero behavioral effect on the party the framing identifies as most at risk.
- **Likelihood:** Medium
- **Impact if realized:** High
- **Mitigation signal:** Run the cheapest possible test before committing the grammar: show a model two versions of the same conventions file and ask it to sort lines into the four piles, or to state what it knows about the line's grounding. If it cannot distinguish, the fix is in the surrounding wording, not the field name.

**Risk 3: "Absence of annotation means human authorship" is an invariant nothing enforces, and content edits break it silently**
- **Category:** Technical
- **Description:** The fourth pile depends entirely on a by-construction claim that the kit never writes a bare line. Three ways it breaks. (a) Legacy: every artifact already in the wild has bare skeleton bullets, so on those files the invariant is inverted — bare means kit-written. (b) Future code paths: any new emitter that forgets an annotation silently manufactures a fake "human-authored" line, and nothing detects it, because the check is deferred. (c) The worst one: hand editing is *invited*. A human who rewrites the text of a kit-written line while leaving the annotation intact produces a line whose annotation vouches for wording the cited source never contained. That is exactly the original failure — a record lying about why a rule is trusted — re-created inside the new grammar, and it is arguably worse because the reader has been told the metadata is now trustworthy.
- **Likelihood:** High
- **Impact if realized:** High
- **Mitigation signal:** Decide explicitly what an annotation vouches for — the source existing at that date, or this exact sentence being supported by it — and say so in the grammar. Accept that the fourth pile is heuristic, not construction, and word the file's own legend accordingly rather than claiming certainty the mechanism cannot deliver.

**Risk 4: Migration of existing artifacts has no path that does not violate a stated "must not"**
- **Category:** Technical
- **Description:** Files already exist containing `verified:` at the old `schema_version`. The success criterion is "zero occurrences of the old `verified:` field in generated output" — which is satisfied by newly generated files while every existing install keeps the dishonest field forever. If instead something rewrites `verified:` to the new event field in place, that is mechanically converting an unbacked state-claim into a dated event-claim about a read that may never have happened — close to the forbidden "silently rewrite a date without something having been re-checked." If setup regeneration is the migration path, it collides with hand editing being invited: regeneration either clobbers team decisions or has to merge, and no merge strategy is specified. This is the integration point where the direction's own rules deadlock.
- **Likelihood:** High
- **Impact if realized:** Medium
- **Mitigation signal:** Write the v1-file behavior down as part of this MVP, not later: what does a reader do when it sees the old schema_version, and does the old file get annotated as "grammar predates this guarantee" rather than migrated at all? Leaving old files legibly old is probably the honest answer and it needs to be a decision, not an omission.

**Risk 5: The empty run-record slot violates the direction's own standing constraint**
- **Category:** Scope
- **Description:** Item 6 defines a grammar slot for a dated run record that nothing will fill, while the standing constraint says "no new field ships that setup cannot fill from something real" and the excluded list bans "reserved field for a future snapshot reference." The slot is a reserved field with a different name. It also repeats the exact failure the direction is correcting: `schema_version` was written by everything and read by nothing, and is now cited as the mistake. Shipping an always-empty run record teaches the same lesson — that parts of this file are decorative — inside the change meant to stop teaching it. Worse, an empty record reads as "no problems found" to a reader who does not know it is unfillable.
- **Likelihood:** Medium
- **Impact if realized:** Medium
- **Mitigation signal:** Cut item 6 from the MVP. If the shape of the record is genuinely needed to constrain later work, put it in the design record, not in the emitted artifact.

**Risk 6: "No code" is inaccurate; the contract clause fans out into every skill**
- **Category:** Scope
- **Description:** The direction is sold as "no code, no network, no new enforcement," but the MVP requires changing setup's writer, changing threshold emission, changing skeleton emission, adding a non-200 check in the fetch path, adding a reader for `schema_version`, and item 7 — a clause added to the contract *every skill copies*. That last one is the highest fan-out edit in the kit: every skill file, every skill's output expectations, and any golden or snapshot tests over generated artifacts. The perceived cheapness is what justified choosing this over alternatives; if the real cost is "touch every skill plus the setup writer plus a schema reader," the comparison that produced this direction was made on a wrong price.
- **Likelihood:** Medium
- **Impact if realized:** Medium
- **Mitigation signal:** Count the actual files the contract clause lands in before committing, and re-check whether the direction still wins at that price. If the clause is the expensive half and the field rename is the cheap half, consider whether they must ship together.

**Risk 7: Suppressing annotations on non-200 converts transient network failures into permanent ungrounded lines**
- **Category:** Technical
- **Description:** Item 5 makes setup emit no source annotation when a fetch returns non-200. A 429 rate-limit, a 503, a corporate proxy interstitial, or a captive portal during a single setup run now produces lines that read as ungrounded forever, with no record of the difference between "no source exists" and "the fetch failed at 14:02 that Tuesday." The reader cannot distinguish a genuinely model-knowledge line from a line whose doc fetch was rate-limited, and the failure is invisible to the person running setup unless setup says something. A doc site that rate-limits after the first few fetches would degrade a whole conventions file at once.
- **Likelihood:** Medium
- **Impact if realized:** Medium
- **Mitigation signal:** Decide whether setup surfaces fetch failures to the operator at run time, and whether a failed fetch is distinguishable in the file from a never-attempted one. At minimum, retry once and tell the human what did not resolve while they are still sitting there.

### Top Concern

**What is the single biggest risk in this direction?**
The direction produces information and defers every mechanism that produces action, then justifies the deferral with evidence it has no way to collect. The framing is explicit that the expected outcome is demotion — most flagged lines should end up demoted or deleted — and that a mechanism where nothing ever gets dropped is theatre. This MVP contains nothing that prompts anyone to demote anything: no flagged list, no filled run record, no moment where a reader is confronted with a line. It replaces a standing claim with a dated fact and hopes a human notices the date. Meanwhile the constraint set — no central state, files in other people's repos — makes it structurally impossible to learn whether anyone did. So the "later, separate decision made on evidence" has no trigger, no data source, and no owner, which is the standard shape of a deferral that never resolves. A year from now the honest position will be "we changed a word, we don't know if it helped, and the grammar is now committed in N repos so changing it again is more expensive than it was today."

### Unstated Assumptions

- **Assumption:** A reader — especially an agent — will interpret an event-word date differently from a state-word date.
  **Why it matters if wrong:** The verb change is declared to be "the substance" of the MVP. If both readings collapse to "someone checked this," the entire change is a rename, the accepted cost (weaker agent-side signal) is paid, and none of the benefit is received.

- **Assumption:** An annotation stays truthful as long as its source is unchanged — i.e. the rule text next to it does not drift.
  **Why it matters if wrong:** Hand editing is explicitly invited. A human rewriting a kit line while leaving the annotation attached creates a line that cites a source for a claim the source never made. That is the original problem with a new field name, and this direction contains no mechanism that could ever notice it.

- **Assumption:** Deferring the classifier is cheap and reversible.
  **Why it matters if wrong:** Grammar ships into other people's committed git history. Every install that adopts v2 raises the cost of v3 — a second migration, a second schema bump, a second set of legacy files. Deferral usually reduces cost; here it may increase the cost of the deferred thing, which inverts the argument for deferring.

- **Assumption:** The single observed 404 is representative of how sources fail.
  **Why it matters if wrong:** The entire problem was surfaced by one dead URL caught by chance. If the dominant real-world failure is not "URL 404s" but "URL resolves and the content changed" — which is the more common documentation failure and which no dead-link check would ever catch — then even the deferred classifier addresses the minority case, and this MVP's grammar is optimized around the wrong failure mode.
