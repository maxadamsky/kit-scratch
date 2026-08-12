# Discovery Brief: cited-source-staleness

*A discovery brief — the discover skill's handoff artifact.*

**Created:** 2026-08-12
**Topic:** cited-source-staleness
**Discover Session Status:** Completed

**Reading the finding codes in this document.** Claims below carry a short code naming
which exploration seat produced them: `CON` argued for the smallest change and could read
the code; `PRE` searched the live web and could not see the code; `STR` and `NUL` reasoned
from the problem statement alone with no tools; `OPR` read the operational setup — CI,
hooks, deploy — and could read the code. `risk-pass` is a separate reviewer that saw the
chosen direction but none of the exploration. The code matters because a claim from a seat
that could inspect the code is a different kind of statement from one that could not.

---

## 1. Problem Statement

The delivery kit writes convention and rubric files into each project, annotating every line
with the source it came from and a `verified:` date. Nothing ever re-checks those sources,
and one of them was already a dead URL the day it was written — a 404 shipped and caught
only by chance. The harm is not that rules become wrong; they usually stay right. The harm
is that the record lies about *why* a rule is trusted, and it lies silently, to a reader
that never clicks the link. Because the kit's entire argument is that its records are
trustworthy, a line asserting verification it does not have teaches the reader that all of
the kit's metadata is decorative — which discredits the honest annotations along with the
stale one.

---

## 2. Who Is Affected

**Primary users:** the *agent* reading the artifact. It treats `verified:` as a fact and
reviews work against a rule whose grounding evaporated, with no path to noticing because it
never follows the link. This is the worse case and the one the design must serve.

**Secondary stakeholders:** the person reading the file, who might at least notice a dead
link on clicking it. Most acutely, the person *inheriting* a repository: they read the
conventions as the team's decisions, cannot distinguish a line grounded in a live source
from one grounded in a 404, and cannot ask whoever ran setup because that person has moved
on.

**Scale:** assume real installs rather than one repository. The load is asymmetric by
construction — these files are written once per project and read on every skill run
afterward, so the read count grows without bound while the verification count stays at one.

---

## 3. The Opportunity

Someone who did not run setup can look at any line and see whether its grounding is live
and, separately, whether it was ever grounded at all — without opening forty URLs or leaving
the file. The file stops being a single all-or-nothing trust object, where today the only
available moves are to believe it wholesale or re-derive it from scratch, and re-deriving is
expensive enough that people simply believe it.

The outcome being optimized for is **honest artifacts as an end in itself — explicitly not
review quality.** The rules usually stay right, so the review-quality gain probably does not
exist, and downstream work must not optimize for it. The goal is narrower and harder: when a
line makes a claim about its own grounding, that claim is true, and when it cannot be true,
the line says so instead of pretending.

---

## 4. Chosen Direction

**Direction:** Fix the artifact's honesty in the annotation grammar alone — no code, no
network, no new enforcement — then decide separately, later, whether a mechanical classifier
is needed.

**What it is:**
The annotation stops asserting a *state* and starts recording an *event*. Instead of
claiming a line is `verified:`, it records that a source was **read on** a date — a fact
that stays true forever and asserts nothing about today. Lines that were never grounded at
all (model-knowledge conventions, scaffold-default numeric thresholds) drop the field
entirely and read as ungrounded, which fixes a case where the kit currently stamps a
verification date on coverage numbers nobody verified against anything. Every line the kit
writes gains an annotation, including skeleton bullets that currently ship bare, so that a
line with no annotation signals human authorship. No expiry date is computed and no shelf
life is stated, because any figure the kit picked would be a date it could not justify — the
same defect at lower stakes.

**Why this direction:**
The honest fix is mostly a deletion and needs no permission from anything: stop writing a
state-word the kit cannot back, annotate the lines it currently ships bare, and the artifact
stops lying without a line of code, a network call, or a decision anyone has to be present
for. The enforcement half is the part nobody yet knows they need — whether a reader told "a
source last read fourteen months ago" ever acts on it is an empirical question with no data
on either side, and the grammar-only change is the cheapest way to find out. Building
enforcement first would impose a ritual before knowing whether the prompt works, in a system
whose only enforcement paths turn a trust problem into an outage.

---

## 5. What Was Considered and Not Chosen

| Direction | Why Not Selected |
|---|---|
| Offline classifier subcommand in the existing runtime (`CON-2`, fetch component `PRE-3`) | **Deferred, not rejected.** It is the natural second step and the only candidate that makes the check mechanically fail. Sequenced behind the grammar change so the decision to build it can be made on evidence about whether readers act on the annotation at all. |
| Snapshot the source at verification time — Robust Links `versiondate`/`versionurl` (`PRE-2`) | Deferred, and deliberately given no reserved field. It is the only mechanism anyone found that makes demotion an *informed* decision rather than a guess, because the reader can see what the source said when the line was written. Rejected for now because it needs network at write time and a third-party archive dependency, both against the offline-by-default constraint. Adopting it later costs a second schema bump. |
| Link-rot checking as the primary mechanism (`PRE-3`) | Reaches only the loudest and rarest case, the 404, and only on documentation-tier lines. Does nothing for never-grounded lines and nothing for a source that still resolves but no longer supports the claim. |
| Content-hash or lockfile-style pinning | Rejected at framing. These detect *change*, and change is not the failure: a source can be rewritten wholesale and still support the claim, or be byte-identical while the claim was a misreading from the start. |
| Do not build — assert less (`NUL-2`) | **Partly accepted, partly declined.** Accepted: never emit a source annotation for a fetch that failed, which is the only thing that would have prevented the originating 404. Declined: the claim that the format should stop asserting grounding entirely, on the grounds the argument's own steelman supplies — demotion needs a tier to demote *into*, and a bare URL cannot say "this was grounded and no longer is." |

*Note: "Not chosen" does not mean "wrong" — these may be valid future phases or worth
revisiting if constraints change.*

---

## 6. Key Trade-offs Resolved

### Shelf life: no policy at all

**Options considered:**
- Compute an expiry date per tier — twelve months for documentation, six for
  community-sourced material (`CON-1`, which flagged this as its own weakest point).
- Keep an expiry field but fill it only where something real determines it, leaving it
  absent otherwise.
- Write no expiry at all and let the reader apply their own judgment to the date.

**Decision:** No expiry field and no stated policy.

**Rationale:** Any figure the kit picked would be a date it cannot justify — the same sin
being fixed, at lower stakes. The fill-only-when-real option was rejected on inspection:
none of this project's four sources publishes a validity window, so the field would ship
absent on effectively every line, which is the field-nobody-fills problem already rejected
elsewhere in this session. HTTP cache headers were considered and rejected as describing CDN
behaviour rather than content validity.

### The verb: an event, not a state

**Options considered:**
- Keep `verified:` and simply remove the policy around it.
- Replace it with a field recording that a source was read on a date.

**Decision:** Replace it. The field records a read event.

**Rationale:** `verified` names a state, and a state-word invites the reader to hear a
standing guarantee — which is precisely the premise challenge's case. Removing the policy
while keeping the word would leave the misleading token and delete the only thing qualifying
it. An event-word states a fact that stays true and asserts nothing about now, which
satisfies the demand to stop asserting without giving up the date that demotion needs.

### Enforcement: may fail, but only where someone went looking

**Options considered:**
- The eventual check never blocks and only reports (`CON-2` made buying the classifier
  conditional on exactly this).
- It blocks, but only inside the human-triggered pass.
- It blocks at the shared preflight gate.

**Decision:** It may genuinely fail, but only within the human-triggered pass — never at the
preflight gate, never inside a hook.

**Rationale:** `OPR-1` and `OPR-4` establish that this system has exactly one status channel
and one enforcement path. Routing a freshness verdict into either converts a trust problem
into an outage: every install loses every skill over an old date, diagnosed from a one-word
error, recoverable only through a conversational setup interview. A check that can fail is
required by the constraints; a check that can take the system down is not.

### Recoverability: no reserved field

**Options considered:** reserve a snapshot field now and leave it unfilled; add it later if
snapshotting is adopted; rule snapshotting out entirely.

**Decision:** Reserve nothing. Add it if and when it is built.

**Rationale:** An unfilled field would be the kit asserting structure it is not backing,
which is the defect under repair. Accepted cost: adopting snapshotting later means a second
schema bump and migration.

### The same-day expiry cliff: dissolved rather than mitigated

**Options considered:** per-source scoping to shrink the triage set; staggered dates; accept
the cliff.

**Decision:** No date-derived behaviour exists in this phase, so the cliff does not arise.
Recorded explicitly as the enforcement phase's problem, with the constraint that this phase
must bake in no assumption of uniform dates.

**Rationale:** `CON-1` and `STR-4` independently derived that because setup writes every
line in one run, every line would expire on one day — a step function rather than a
distribution. There is no cliff without a policy converting uniform dates into a uniform
expiry event, and this direction has no such policy.

---

## 7. Scope Sketch

**MVP — what the first release must include:**

1. Replace the `verified:` field with a field recording that a source was **read on** a
   date. No expiry, no computed staleness, no stated shelf life.
2. Model-knowledge lines and scaffold-default thresholds drop the field entirely and read as
   ungrounded. This fixes a confirmed live defect — coverage thresholds currently carry a
   verification date against nothing.
3. Every line the kit writes carries an annotation, including the skeleton bullets that
   currently ship bare, so absence of an annotation signals human authorship.
4. The schema version is bumped **and actually read**, following the existing pattern that
   already reads one frontmatter line offline to decide freshness.
5. Setup never emits a source annotation for a fetch that returned a non-200 response.
6. The grammar states the **rule** for a run record without emitting an empty one: when a
   verification pass runs it writes an itemised dated record distinguishing checked,
   unreachable, and never-grounded, and **absence of a record means no pass has ever run.**
   Nothing is emitted until something real fills it.
7. An annotation's promise is stated explicitly in the file's own legend: it claims that
   someone read this source on this date **and that this line follows from it**. The legend
   states the editor's obligation — editing the text of an annotated line obliges you to
   update or drop its annotation — and states that the human-authored distinction is
   **heuristic, not guaranteed.**
8. One clause added to the contract every skill copies: a finding citing a line states when
   its source was last read rather than implying currency.

**Validation step, before the grammar is committed:** show a model two versions of the same
conventions file and ask it to sort the lines by grounding. If it cannot distinguish an
event-word date from a state-word date, the fix belongs in the surrounding wording rather
than the field name — and the accepted cost of a weaker agent-side prompt would otherwise be
paid for nothing.

**Explicitly excluded from this phase:**

- The classifier subcommand and source snapshotting — both deferred by the sequencing
  decision.
- Any automated fetching, re-dating, or scheduled job.
- Anything touching the setup preflight gate, the write-guard hook, or CI.
- Any reserved field for a future snapshot reference.

*Note: Exclusions are not permanent — they are scope boundaries for this phase.*

---

## 8. Success Criteria

- **Primary test.** A person who did not run setup sorts every line in the conventions and
  gates files into grounded / ungrounded / human-authored, offline, without leaving the
  file. The first two distinctions hold by construction; the human-authored one is
  heuristic and the file says so; the expired distinction is the reader's judgment rather
  than a fact the file asserts. If this does not hold, nothing shipped that matters.
- **No line asserts verification.** Zero occurrences of the old `verified:` field in
  generated output, and every kit-written line carries an annotation. Both halves are
  mechanically checkable by grep.
- **The schema version is read by something.** Today it is written into every artifact and
  consumed by nothing — the same defect in miniature. A new grammar that ships without
  wiring it fails the blast-radius constraint on day one.

---

## 9. Constraints

- **Node only, no shell.** Anything executable is a Node script under the kit's shared
  runtime. The kit is macOS-proven and untested on Windows and Linux, and Windows is where
  shell assumptions break first. A solution that needs a shell does not ship.
- **Offline by default.** Assume no network at review time; treat its presence as a bonus. A
  check that only works online makes the artifact honest on connected machines and silent
  everywhere else. Fetching, if any, belongs in an explicit human-triggered pass — not a
  hook, not a skill run, not CI.
- **No central state.** These files live in other people's repositories, committed to their
  git history, touched only when a skill runs. There is no registry, no database, no
  kit-side record of what was verified when. Whatever the mechanism knows must be inside the
  artifact or it does not exist. This rules out anything shaped like a service.
- **Hand editing is invited, not tolerated.** User edits are treated as team decisions, so
  the mechanism must survive a human rewriting a line, deleting an annotation, or adding a
  convention with no annotation at all. It cannot assume the kit wrote everything it reads.
- **Existing files must stay readable.** The grammar may change, but a file written under
  the old grammar must never become unparseable or silently misread, and must declare which
  grammar it was written under.
- **Interpretable without kit internals.** No network, no source catalog, no knowledge of
  how the kit works.
- **Must not add a check that cannot fail.** A mechanism that can only ever say "fine" is
  decoration, and worse than nothing because it looks like assurance.
- **Must not silently re-date without a real re-check.** Refreshing the date is the
  dishonest act; the stale date is not.
- **Standing design constraint:** no new field ships that setup cannot fill from something
  real. This is the general form of the mistake that killed the expiry field, and it applies
  past this work.

---

## 10. Risks Acknowledged

Identified by the Phase 2b risk pass — **one independent perspective, not complete
coverage.** Full inventory at `.ai-delivery/features/cited-source-staleness/risk-challenge.md`.
"Independently re-found" means a reviewer that never saw the exploration reached the same
conclusion from different context, which is the strongest attention signal this process
produces.

| Risk | Category | Likelihood | Impact | Mitigation Signal | Found By |
|---|---|---|---|---|---|
| The deferral's evidence can never be collected — no telemetry, no registry, files in other people's repos, so "decide later on evidence" has no trigger, no data source, no owner | Assumption | High | High | Name the specific observation that triggers the follow-on decision and where it comes from, or drop the evidence framing and admit this is a standing design choice | risk-pass; re-found `OPR-3` |
| The absence-means-human rule is unenforced, and invited hand-editing breaks it silently — a human who rewrites an annotated line's text leaves an annotation vouching for wording the source never contained | Technical | High | High | Partly addressed in scope item 7: state what the annotation promises, state the editor's obligation, and admit the distinction is heuristic. Nothing detects a violation | risk-pass (new); legacy-file half re-found `STR-6` |
| The verb change is an untested linguistic bet, and the primary reader is a model that may flatten event and state into "someone checked this" | Assumption | Medium | High | The validation step added to scope — test a model's sorting on both versions before committing the grammar | risk-pass (new) |
| Migration of existing files has no path that does not violate a stated must-not — regenerate and clobber invited edits, rewrite in place and silently re-date, or leave every install dishonest forever | Technical | High | Medium | Decide old-file behaviour inside this phase. Leaving old files legibly old, annotated as predating the guarantee, is probably the honest answer | risk-pass; re-found `STR-5`, `STR-6` |
| "No code" is inaccurate — the contract clause lands in every skill file, and the perceived cheapness is what priced this direction as the winner | Scope | Medium | Medium | Count the files the clause actually touches before committing, and re-check whether the direction still wins at that price | risk-pass (new) |
| Suppressing annotations on a failed fetch turns transient network failures into permanently ungrounded lines — a rate-limit during one setup run is indistinguishable from a source that never existed | Technical | Medium | Medium | Decide whether setup surfaces fetch failures to the operator at run time, and whether a failed fetch is distinguishable in the file from one never attempted. Retry once and say what did not resolve | risk-pass; re-found `STR-1` (inverted — the same mechanism causing wrongful ungrounding at authoring time rather than wrongful expiry at check time) |

Two risks were resolved during direction setting rather than carried: the empty run-record
slot (scope item 6 rewritten as a rule that emits nothing) and the undefined annotation
promise (scope item 7 added).

---

## 11. Council Insights Summary

**Exploration roster:** constraint, precedent, stress, null, operator (full configured
roster; no degraded flags, no failures, no retries).

**Synthesis basis:** 5 of 5 mandates examined

**Coverage gaps:** None — every configured mandate examined.

**Premise challenge:** `NUL-1` — the toolkit was never entitled to print a date at all,
because a format promising continuous grounding from a one-shot fetch will lie regardless of
what policy governs its expiry — **partly accepted.** Accepted: never emit a source
annotation for a fetch that failed, which is the only thing that would have prevented the
originating 404. Declined: that the format should stop asserting grounding entirely, on the
grounds the argument's own steelman supplies — demotion needs a tier to demote into, and a
bare URL cannot say "this was grounded and no longer is."

**Convergences** (across seats with disjoint evidence — raises attention, never confidence):

- **The same-day expiry cliff.** `CON-1` (code) and `STR-4` (problem statement only)
  independently derived that one setup run writes every line, so every line would expire
  together as a step function. The *outcome* was already in the problem statement and is an
  echo; the *mechanism* and its per-source mitigation appear in neither.
- **Unparseable input must fail closed.** `STR-3` derived that malformed annotations would
  classify as still-grounded, and `CON-2` independently required that anything unparseable
  classify as unannotated rather than be dropped. Recorded with the caveat that the stated
  must-not sits close to this, so part of the agreement may be echo.

**Worth remembering:**

- Four claims were adjudicated by direct inspection during synthesis, and three confirmed
  live defects: coverage thresholds carry a verification date against nothing; the kit ships
  unannotated lines, so absence does not currently mean human authorship; and the schema
  version is read by no script or hook while an adjacent function proves the technique works
  offline.
- `PRE-1` found that Wikipedia's citation-and-verifiability templates are simultaneously the
  closest precedent for the four-way sort and the loudest warning against it — its
  citation-needed backlog is the "flagged lines nobody triages" outcome, already run at
  scale for twenty years. The backlog figure itself is **recalled and unverified**, so it
  grounds attention rather than a conclusion.
- `PRE-2` reported that the Robust Links specification's canonical host failed DNS
  resolution during the session and that the spec self-describes as under experimental
  revision — a specification worth copying, not depending on.
- **What no seat could see:** actual user behaviour (whether real installs triage or
  rubber-stamp — the load-bearing uncertainty in both the premise challenge and the success
  metric); non-macOS behaviour; and the W-16 row itself, known here only through paraphrase.

---

## 12. Prior Art and Context

- **Inside the kit: nothing built.** An open row, W-16, covers this ground — motivated by a
  different instance, where Databricks renamed Asset Bundles to Declarative Automation
  Bundles in March 2026 and shipped content referred to a product name that no longer
  existed. That row proposes a three-month volatile clock plus source-and-date metadata. The
  clock was never built. An annotation format resembling the metadata half does appear in
  generated output, but **whether it was implemented from W-16 or arrived independently is
  not known, and no lineage should be asserted.**
- **Certificate expiry — transfers.** Explicit expiry inside the artifact, evaluated offline
  with no network and no registry, failing loudly rather than degrading quietly. This is the
  model the direction follows in spirit, minus the computed expiry date.
- **Lockfile and content-hash pinning — do not transfer.** They detect change, and change is
  not the failure.
- **Link-rot tooling — partial.** Catches the loudest and rarest case and reaches only
  documentation-tier lines.
- **Docs-as-tests — near-miss.** Makes claims fail-able, but these are prose conventions;
  forcing them to be runnable would change what the artifact is.
- **Wikipedia's maintenance templates** (`PRE-1`) and **Robust Links** (`PRE-2`) are the two
  external precedents worth reading before implementation. **linkinator** is the Node-API
  link checker candidate for the eventual fetch pass; **lychee** is eliminated by the
  no-shell constraint because it is a Rust binary requiring exec.

---

## 13. Open Questions

| Question | Why It Matters | Owner |
|---|---|---|
| What specific observation triggers the decision to build the enforcement phase, and where does it come from? | This is the risk pass's top concern. Without a named trigger, data source, and owner, "decide later on evidence" is a deferral that never resolves — and the grammar gets more expensive to change with every install that adopts it | Kit maintainer |
| What actually happens to files written under the old grammar? | Every migration path available appears to violate a stated must-not. Leaving old files legibly old is probably the honest answer, but it must be a decision rather than an omission | Kit maintainer |
| What is the new field literally called? | The session settled the *semantics* — an event, not a state — but never fixed the token. The name is the whole mechanism for a reader who sees nothing else | Kit maintainer |
| Does a model actually sort differently given an event-word date versus a state-word one? | The verb change is declared to be the substance of this work, and the primary reader is an agent. If the distinction collapses, the change is a rename and the accepted cost buys nothing. Cheap to test | Validation step, before the grammar is committed |
| How many files does the contract clause touch? | The direction was chosen partly because it was priced as cheap. If the clause lands in every skill file plus tests, the comparison that selected it was made on a wrong number | Kit maintainer |
| Can a failed fetch be distinguished in the file from a source that was never attempted? | Without this, one rate-limited setup run permanently mislabels lines as ungrounded, and nobody learns it happened | Kit maintainer |
| Is the 404 representative of how sources actually fail? | If the dominant real failure is "resolves but the content changed," then even the deferred enforcement addresses the minority case and the grammar is optimized around the wrong failure mode | Kit maintainer |

---

*Generated by the discover skill. See `.ai-delivery/features/cited-source-staleness/` for all
session artifacts including the raw exploration responses.*
